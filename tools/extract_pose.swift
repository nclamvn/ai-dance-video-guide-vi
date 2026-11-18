import Foundation
import AVFoundation
import Vision
import CoreVideo

let args=CommandLine.arguments
if args.count != 4 { fputs("usage: swift extract_pose.swift input output intervalSeconds\n",stderr);exit(2) }
let asset=AVURLAsset(url:URL(fileURLWithPath:args[1]))
let tracks=asset.tracks(withMediaType:.video)
guard let track=tracks.first else { fatalError("No video") }
let reader=try AVAssetReader(asset:asset)
let output=AVAssetReaderTrackOutput(track:track,outputSettings:[kCVPixelBufferPixelFormatTypeKey as String:kCVPixelFormatType_32BGRA])
output.alwaysCopiesSampleData=false
reader.add(output)
let interval=Double(args[3])!
let joints:[(String,VNHumanBodyPoseObservation.JointName)]=[("nose",.nose),("neck",.neck),("root",.root),("leftShoulder",.leftShoulder),("rightShoulder",.rightShoulder),("leftElbow",.leftElbow),("rightElbow",.rightElbow),("leftWrist",.leftWrist),("rightWrist",.rightWrist),("leftHip",.leftHip),("rightHip",.rightHip),("leftKnee",.leftKnee),("rightKnee",.rightKnee),("leftAnkle",.leftAnkle),("rightAnkle",.rightAnkle)]
var records:[[String:Any]]=[]
var next=0.0
reader.startReading()
while let sample=output.copyNextSampleBuffer(){
 let time=CMTimeGetSeconds(CMSampleBufferGetPresentationTimeStamp(sample))
 if time+0.001 < next { continue }
 next=time+interval
 autoreleasepool {
  guard let pixel=CMSampleBufferGetImageBuffer(sample) else { return }
  let request=VNDetectHumanBodyPoseRequest()
  do {
   try VNImageRequestHandler(cvPixelBuffer:pixel,orientation:.up,options:[:]).perform([request])
   var row:[String:Any]=["time":time]
   if let body=request.results?.max(by:{$0.confidence<$1.confidence}) {
    var pts:[String:[Double]]=[:]
    for (name,joint) in joints {
     if let p=try? body.recognizedPoint(joint){pts[name]=[p.location.x,p.location.y,Double(p.confidence)]}
    }
    row["points"]=pts;row["confidence"]=Double(body.confidence)
   }
   records.append(row)
  } catch { records.append(["time":time,"error":String(describing:error)]) }
 }
}
if reader.status == .failed { fatalError(String(describing:reader.error)) }
let data=try JSONSerialization.data(withJSONObject:["input":args[1],"method":"Apple Vision VNDetectHumanBodyPoseRequest; local inference, no network; estimated keypoints require visual review","interval":interval,"samples":records],options:[.prettyPrinted,.sortedKeys])
try data.write(to:URL(fileURLWithPath:args[2]))
print("samples=\(records.count) output=\(args[2])")
