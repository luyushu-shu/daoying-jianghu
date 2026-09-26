#!/usr/bin/env python3
"""
Generate Unity Animation Clips (.anim) and AnimatorController for Mook Swordsman (杂兵刀手).
- MookIdle.anim: looping breathing idle (4 frames @ 5fps = 0.20s per frame, 0.80s total)
- MookWalk.anim: looping walk cycle (4 frames @ 6.67fps = 0.15s per frame, 0.60s total)
- MookAttackA.anim: one-shot slash attack (4 frames @ 7.14fps = 0.14s per frame, 0.56s total)
- MookSwordsman.controller: AnimatorController state machine with Speed float and AttackA trigger.
"""
from pathlib import Path
import re
import uuid

BASE_DIR = Path(r"c:\Users\luyus\Desktop\刀影江湖\New Tuanjie Project\Assets\Sprites\Enemies\MookSwordsman")

def get_guid(meta_path):
    text = meta_path.read_text(encoding="utf-8")
    m = re.search(r"guid:\s*([a-zA-Z0-9+=/]+)", text)
    if m:
        return m.group(1).strip()
    raise ValueError(f"No guid found in {meta_path}")

def make_anim_meta(guid):
    return f"""fileFormatVersion: 2
guid: {guid}
NativeFormatImporter:
  externalObjects: {{}}
  mainObjectFileID: 7400000
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""

def make_anim_clip(name, frame_guids, frame_duration, loop=True):
    total_time = len(frame_guids) * frame_duration
    sample_rate = 1.0 / frame_duration
    
    curve_points = []
    pptr_mappings = []
    
    for i, g in enumerate(frame_guids):
        t = i * frame_duration
        curve_points.append(f"""    - time: {t:.4f}
      value: {{fileID: 21300000, guid: {g}, type: 3}}""")
        pptr_mappings.append(f"    - {{fileID: 21300000, guid: {g}, type: 3}}")
        
    curve_str = "\n".join(curve_points)
    pptr_str = "\n".join(pptr_mappings)
    loop_val = 1 if loop else 0
    
    return f"""%YAML 1.1
%TAG !u! tag:yousandi.cn,2023:
--- !u!74 &7400000
AnimationClip:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: {name}
  serializedVersion: 11
  m_Legacy: 0
  m_Compressed: 0
  m_UseHighQualityCurve: 1
  m_RotationCurves: []
  m_CompressedRotationCurves: []
  m_EulerCurves: []
  m_PositionCurves: []
  m_ScaleCurves: []
  m_FloatCurves: []
  m_PPtrCurves:
  - serializedVersion: 2
    curve:
{curve_str}
    attribute: m_Sprite
    path: 
    classID: 212
    script: {{fileID: 0}}
    flags: 2
  m_SampleRate: {sample_rate:.4f}
  m_WrapMode: 0
  m_Bounds:
    m_Center: {{x: 0, y: 0, z: 0}}
    m_Extent: {{x: 0, y: 0, z: 0}}
  m_ClipBindingConstant:
    genericBindings:
    - serializedVersion: 2
      path: 0
      attribute: 0
      script: {{fileID: 0}}
      typeID: 212
      customType: 23
      isPPtrCurve: 1
      isIntCurve: 0
      isSerializeReferenceCurve: 0
    pptrCurveMapping:
{pptr_str}
  m_AnimationClipSettings:
    serializedVersion: 3
    m_AdditiveReferencePoseClip: {{fileID: 0}}
    m_AdditiveReferencePoseTime: 0
    m_StartTime: 0
    m_StopTime: {total_time:.4f}
    m_OrientationOffsetY: 0
    m_Level: 0
    m_CycleOffset: 0
    m_AdditiveType: 0
    m_BasePoseType: 0
    m_AdditiveSelectedAnimation: {{fileID: 0}}
    m_AdditiveSelectedAnimationFrameIndex: 0
    m_HasAdditiveReferencePose: 0
    m_LockToRoot: 0
    m_LoopTime: {loop_val}
    m_LoopBlend: 0
    m_LoopBlendOrientation: 0
    m_LoopBlendPositionY: 0
    m_LoopBlendPositionXZ: 0
    m_KeepOriginalOrientation: 0
    m_KeepOriginalPositionY: 1
    m_KeepOriginalPositionXZ: 0
    m_HeightFromFeet: 0
    m_Mirror: 0
  m_EditorCurves: []
  m_EulerEditorCurves: []
  m_HasGenericRootTransform: 0
  m_HasMotionFloatCurves: 0
  m_Events: []
  m_Intervals: []
  m_ACLContext:
    ACLCompressionLevel: 0
    ACLCurvePrecision: 0.01
    UseACLCurve: 0
    UseACLFastSampleMode: 1
  m_MuscleEncodeContext:
    type: 0
    rotationError: 0
    positionError: 0
    scaleError: 0
"""

def make_controller(idle_guid, walk_guid, attack_guid):
    return f"""%YAML 1.1
%TAG !u! tag:yousandi.cn,2023:
--- !u!91 &9100000
AnimatorController:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: MookSwordsman
  serializedVersion: 6
  m_AnimatorParameters:
  - m_Name: Speed
    m_Type: 1
    m_DefaultFloat: 0
    m_DefaultInt: 0
    m_DefaultBool: 0
    m_Controller: {{fileID: 9100000}}
  - m_Name: AttackA
    m_Type: 9
    m_DefaultFloat: 0
    m_DefaultInt: 0
    m_DefaultBool: 0
    m_Controller: {{fileID: 9100000}}
  m_AnimatorLayers:
  - serializedVersion: 5
    m_Name: Base Layer
    m_StateMachine: {{fileID: 110700000}}
    m_Mask: {{fileID: 0}}
    m_Motions: []
    m_Behaviours: []
    m_BlendingMode: 0
    m_SyncedLayerIndex: -1
    m_DefaultWeight: 0
    m_IKPass: 0
    m_SyncedLayerAffectsTiming: 0
    m_Controller: {{fileID: 9100000}}
--- !u!1101 &110100001
AnimatorStateTransition:
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: 
  m_Conditions:
  - m_ConditionMode: 3
    m_ConditionEvent: Speed
    m_EventTreshold: 0.1
  m_DstStateMachine: {{fileID: 0}}
  m_DstState: {{fileID: 110200002}}
  m_Solo: 0
  m_Mute: 0
  m_IsExit: 0
  serializedVersion: 3
  m_TransitionDuration: 0.05
  m_TransitionOffset: 0
  m_ExitTime: 0.75
  m_HasExitTime: 0
  m_HasFixedDuration: 1
  m_InterruptionSource: 0
  m_OrderedInterruption: 1
  m_CanTransitionToSelf: 1
--- !u!1101 &110100002
AnimatorStateTransition:
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: 
  m_Conditions:
  - m_ConditionMode: 4
    m_ConditionEvent: Speed
    m_EventTreshold: 0.1
  m_DstStateMachine: {{fileID: 0}}
  m_DstState: {{fileID: 110200001}}
  m_Solo: 0
  m_Mute: 0
  m_IsExit: 0
  serializedVersion: 3
  m_TransitionDuration: 0.05
  m_TransitionOffset: 0
  m_ExitTime: 0.75
  m_HasExitTime: 0
  m_HasFixedDuration: 1
  m_InterruptionSource: 0
  m_OrderedInterruption: 1
  m_CanTransitionToSelf: 1
--- !u!1101 &110100003
AnimatorStateTransition:
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: 
  m_Conditions:
  - m_ConditionMode: 1
    m_ConditionEvent: AttackA
    m_EventTreshold: 0
  m_DstStateMachine: {{fileID: 0}}
  m_DstState: {{fileID: 110200003}}
  m_Solo: 0
  m_Mute: 0
  m_IsExit: 0
  serializedVersion: 3
  m_TransitionDuration: 0.02
  m_TransitionOffset: 0
  m_ExitTime: 0.75
  m_HasExitTime: 0
  m_HasFixedDuration: 1
  m_InterruptionSource: 0
  m_OrderedInterruption: 1
  m_CanTransitionToSelf: 1
--- !u!1101 &110100004
AnimatorStateTransition:
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: 
  m_Conditions: []
  m_DstStateMachine: {{fileID: 0}}
  m_DstState: {{fileID: 110200001}}
  m_Solo: 0
  m_Mute: 0
  m_IsExit: 0
  serializedVersion: 3
  m_TransitionDuration: 0.1
  m_TransitionOffset: 0
  m_ExitTime: 0.9
  m_HasExitTime: 1
  m_HasFixedDuration: 1
  m_InterruptionSource: 0
  m_OrderedInterruption: 1
  m_CanTransitionToSelf: 1
--- !u!1102 &110200001
AnimatorState:
  serializedVersion: 6
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: Idle
  m_Speed: 1
  m_CycleOffset: 0
  m_Transitions:
  - {{fileID: 110100001}}
  m_StateMachineBehaviours: []
  m_Position: {{x: 50, y: 50, z: 0}}
  m_IKOnFeet: 0
  m_WriteDefaultValues: 1
  m_Mirror: 0
  m_SpeedParameterActive: 0
  m_MirrorParameterActive: 0
  m_CycleOffsetParameterActive: 0
  m_TimeParameterActive: 0
  m_Motion: {{fileID: 7400000, guid: {idle_guid}, type: 2}}
  m_Tag: 
  m_SpeedParameter: 
  m_MirrorParameter: 
  m_CycleOffsetParameter: 
  m_TimeParameter: 
--- !u!1102 &110200002
AnimatorState:
  serializedVersion: 6
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: Walk
  m_Speed: 1
  m_CycleOffset: 0
  m_Transitions:
  - {{fileID: 110100002}}
  m_StateMachineBehaviours: []
  m_Position: {{x: 50, y: 50, z: 0}}
  m_IKOnFeet: 0
  m_WriteDefaultValues: 1
  m_Mirror: 0
  m_SpeedParameterActive: 0
  m_MirrorParameterActive: 0
  m_CycleOffsetParameterActive: 0
  m_TimeParameterActive: 0
  m_Motion: {{fileID: 7400000, guid: {walk_guid}, type: 2}}
  m_Tag: 
  m_SpeedParameter: 
  m_MirrorParameter: 
  m_CycleOffsetParameter: 
  m_TimeParameter: 
--- !u!1102 &110200003
AnimatorState:
  serializedVersion: 6
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: AttackA
  m_Speed: 1
  m_CycleOffset: 0
  m_Transitions:
  - {{fileID: 110100004}}
  m_StateMachineBehaviours: []
  m_Position: {{x: 50, y: 50, z: 0}}
  m_IKOnFeet: 0
  m_WriteDefaultValues: 1
  m_Mirror: 0
  m_SpeedParameterActive: 0
  m_MirrorParameterActive: 0
  m_CycleOffsetParameterActive: 0
  m_TimeParameterActive: 0
  m_Motion: {{fileID: 7400000, guid: {attack_guid}, type: 2}}
  m_Tag: 
  m_SpeedParameter: 
  m_MirrorParameter: 
  m_CycleOffsetParameter: 
  m_TimeParameter: 
--- !u!1107 &110700000
AnimatorStateMachine:
  serializedVersion: 6
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: Base Layer
  m_ChildStates:
  - serializedVersion: 1
    m_State: {{fileID: 110200001}}
    m_Position: {{x: 200, y: 0, z: 0}}
  - serializedVersion: 1
    m_State: {{fileID: 110200002}}
    m_Position: {{x: 200, y: 100, z: 0}}
  - serializedVersion: 1
    m_State: {{fileID: 110200003}}
    m_Position: {{x: 450, y: 0, z: 0}}
  m_ChildStateMachines: []
  m_AnyStateTransitions:
  - {{fileID: 110100003}}
  m_EntryTransitions: []
  m_StateMachineTransitions: {{}}
  m_StateMachineBehaviours: []
  m_AnyStatePosition: {{x: 470, y: -100, z: 0}}
  m_EntryPosition: {{x: 50, y: 0, z: 0}}
  m_ExitPosition: {{x: 800, y: 120, z: 0}}
  m_ParentStateMachinePosition: {{x: 800, y: 20, z: 0}}
  m_DefaultState: {{fileID: 110200001}}
"""

def main():
    print("Building Unity Animation Clips and Animator Controller...")
    
    # 1. Walk anim
    walk_guids = [get_guid(BASE_DIR / "Walk" / f"walk-{i+1}.png.meta") for i in range(4)]
    walk_anim = make_anim_clip("MookWalk", walk_guids, frame_duration=0.15, loop=True)
    walk_anim_path = BASE_DIR / "Walk" / "MookWalk.anim"
    walk_anim_path.write_text(walk_anim, encoding="utf-8")
    walk_guid = uuid.uuid4().hex
    (BASE_DIR / "Walk" / "MookWalk.anim.meta").write_text(make_anim_meta(walk_guid), encoding="utf-8")
    print(f"  Saved {walk_anim_path} (guid={walk_guid})")
    
    # 2. Attack anim
    attack_guids = [get_guid(BASE_DIR / "AttackA" / f"attack-{i+1}.png.meta") for i in range(4)]
    attack_anim = make_anim_clip("MookAttackA", attack_guids, frame_duration=0.14, loop=False)
    attack_anim_path = BASE_DIR / "AttackA" / "MookAttackA.anim"
    attack_anim_path.write_text(attack_anim, encoding="utf-8")
    attack_guid = uuid.uuid4().hex
    (BASE_DIR / "AttackA" / "MookAttackA.anim.meta").write_text(make_anim_meta(attack_guid), encoding="utf-8")
    print(f"  Saved {attack_anim_path} (guid={attack_guid})")
    
    # 3. Idle anim
    idle_guids = [get_guid(BASE_DIR / "Idle" / f"idle-{i+1}.png.meta") for i in range(4)]
    idle_anim = make_anim_clip("MookIdle", idle_guids, frame_duration=0.20, loop=True)
    idle_anim_path = BASE_DIR / "Idle" / "MookIdle.anim"
    idle_anim_path.write_text(idle_anim, encoding="utf-8")
    idle_guid = uuid.uuid4().hex
    (BASE_DIR / "Idle" / "MookIdle.anim.meta").write_text(make_anim_meta(idle_guid), encoding="utf-8")
    print(f"  Saved {idle_anim_path} (guid={idle_guid})")
    
    # 4. Controller
    ctrl_content = make_controller(idle_guid, walk_guid, attack_guid)
    ctrl_path = BASE_DIR / "MookSwordsman.controller"
    ctrl_path.write_text(ctrl_content, encoding="utf-8")
    ctrl_guid = uuid.uuid4().hex
    (BASE_DIR / "MookSwordsman.controller.meta").write_text(f"""fileFormatVersion: 2
guid: {ctrl_guid}
NativeFormatImporter:
  externalObjects: {{}}
  mainObjectFileID: 9100000
  userData: 
  assetBundleName: 
  assetBundleVariant: 
""", encoding="utf-8")
    print(f"  Saved {ctrl_path} (guid={ctrl_guid})")
    print("\nAll Unity clips and AnimatorController built successfully!")

if __name__ == "__main__":
    main()
