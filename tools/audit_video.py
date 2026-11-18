#!/usr/bin/env python3
"""Offline full-decode audit. FFmpeg required. No semantic approval or network calls."""
import argparse, hashlib, json, math, os, shutil, subprocess, sys
from pathlib import Path

def binary(explicit, name):
    candidate=explicit or shutil.which(name)
    if candidate and Path(candidate).is_file():
        return str(Path(candidate).resolve())
    if explicit:
        raise ValueError("Executable not found: "+explicit)
    return None

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("video",type=Path); p.add_argument("--out",required=True,type=Path)
    p.add_argument("--ffmpeg"); p.add_argument("--ffprobe")
    p.add_argument("--expected-seconds",type=float); p.add_argument("--tolerance-seconds",type=float,default=0.1)
    p.add_argument("--sheets",action="store_true")
    a=p.parse_args()
    try:
        if not a.video.is_file(): raise ValueError("Input video not found")
        if a.expected_seconds is not None and (not math.isfinite(a.expected_seconds) or a.expected_seconds<=0):
            raise ValueError("expected-seconds must be finite and positive")
        if not math.isfinite(a.tolerance_seconds) or a.tolerance_seconds<0:
            raise ValueError("tolerance-seconds must be finite and non-negative")
        ffmpeg=binary(a.ffmpeg,"ffmpeg"); ffprobe=binary(a.ffprobe,"ffprobe")
        if not ffmpeg: raise ValueError("FFmpeg missing: put it on PATH or use --ffmpeg")
        if a.out.resolve()==a.video.resolve(): raise ValueError("Output directory cannot equal input video")
        a.out.mkdir(parents=True,exist_ok=True)
        def portable_error(message):
            return message.replace(str(a.video.resolve()), a.video.name)
        # Keep previous audits intact; never silently overwrite their evidence.
        if (a.out/"audit.json").exists(): raise ValueError("audit.json already exists; choose a new output directory")
        versions={}
        for key,exe in (("ffmpeg",ffmpeg),("ffprobe",ffprobe)):
            if exe:
                versions[key]=subprocess.run([exe,"-version"],capture_output=True,text=True).stdout.splitlines()[0]
        metadata=None; probe_error=None
        if ffprobe:
            pr=subprocess.run([ffprobe,"-v","error","-count_frames","-show_streams","-show_format","-of","json",str(a.video.resolve())],capture_output=True,text=True)
            if pr.returncode: probe_error=portable_error(pr.stderr)
            else: metadata=json.loads(pr.stdout)
        cmd=[ffmpeg,"-hide_banner","-v","error","-xerror","-nostats","-progress","pipe:1",
             "-i",str(a.video.resolve()),"-map","0:v:0","-map","0:a?","-f","null","-"]
        result=subprocess.run(cmd,capture_output=True,text=True)
        progress={}
        for line in result.stdout.splitlines():
            if "=" in line:
                key,value=line.split("=",1); progress[key]=value
        frames=int(progress["frame"]) if progress.get("frame","").isdigit() else None
        raw_time=progress.get("out_time_us")
        seconds=int(raw_time)/1000000 if raw_time and raw_time.lstrip("-").isdigit() else None
        duration_ok=None if a.expected_seconds is None or seconds is None else abs(seconds-a.expected_seconds)<=a.tolerance_seconds
        vstream=next((s for s in (metadata or {}).get("streams",[]) if s.get("codec_type")=="video"),None)
        report={"file_name":a.video.name,"sha256":sha256(a.video),"bytes":a.video.stat().st_size,
                "tool_versions":versions,"full_decode_exit_code":result.returncode,
                "decode_complete":result.returncode==0 and not result.stderr.strip() and progress.get("progress")=="end" and (frames or 0)>0,
                "decoder_error_output_present":bool(result.stderr.strip()),
                "decoded_video_frames":frames,"decoded_mux_timeline_end_seconds":seconds,
                "duration_note":"FFmpeg output end includes mapped audio. VFR timing must be read from timestamps, not frame/fps.",
                "expected_seconds":a.expected_seconds,"tolerance_seconds":a.tolerance_seconds,"duration_within_tolerance":duration_ok,
                "video_stream":vstream,"metadata_status":"PROBED" if metadata is not None else "UNVERIFIED",
                "probe_error":probe_error,"decode_errors":portable_error(result.stderr),
                "semantic_visual_review":"NOT_PERFORMED","audio_sync_review":"NOT_PERFORMED",
                "overall_acceptance":"NOT_EVALUATED","sheets":None}
        if a.sheets and report["decode_complete"]:
            free=shutil.disk_usage(a.out).free
            if free<10*1024**3: raise ValueError("Less than 10 GiB free; not creating sheets")
            sheet_dir=a.out/"sheets"
            if sheet_dir.exists(): raise ValueError("sheets directory exists; choose a new output directory")
            sheet_dir.mkdir()
            vf="scale=240:426:force_original_aspect_ratio=decrease,pad=240:426:(ow-iw)/2:(oh-ih)/2,tile=5x4:padding=2:margin=2"
            sr=subprocess.run([ffmpeg,"-hide_banner","-v","error","-xerror","-i",str(a.video.resolve()),
               "-map","0:v:0","-an","-vf",vf,"-fps_mode","passthrough","-q:v","3",str(sheet_dir/"sheet-%04d.jpg")],
               capture_output=True,text=True)
            sheets=sorted(sheet_dir.glob("sheet-*.jpg"))
            expected=math.ceil(frames/20) if frames is not None else None
            index=[{"file":"sheets/"+s.name,"first_frame":i*20,
                    "last_frame":min((i+1)*20-1,frames-1),"order":"row_major","timestamp_policy":"Use PTS for VFR"}
                   for i,s in enumerate(sheets)]
            (a.out/"sheet-index.json").write_text(json.dumps(index,indent=2),encoding="utf-8")
            report["sheets"]={"exit_code":sr.returncode,"created":len(sheets),"expected":expected,
                              "coverage_count_matches":len(sheets)==expected,"errors":portable_error(sr.stderr),
                              "note":"Last sheet may contain blank unused cells. Review native-resolution regions separately."}
        if metadata is not None:
            # Strip local absolute filename from portable metadata report.
            metadata.get("format",{}).pop("filename",None)
            (a.out/"probe.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding="utf-8")
        failed=not report["decode_complete"] or duration_ok is False or (
           report["sheets"] is not None and (report["sheets"]["exit_code"]!=0 or not report["sheets"]["coverage_count_matches"]))
        report["structural_checks_requested"]="FAIL" if failed else "PASS"
        (a.out/"audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        print(json.dumps(report,ensure_ascii=False,indent=2))
        return 1 if failed else 0
    except (ValueError,OSError,json.JSONDecodeError) as e:
        print(json.dumps({"status":"SETUP_ERROR","error":str(e)},ensure_ascii=False))
        return 2

if __name__=="__main__":
    sys.exit(main())
