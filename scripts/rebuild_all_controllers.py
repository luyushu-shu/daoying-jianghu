import re

def build_unified_controller_text(default_state_id=110200001, controller_name="PlayerIdle"):
    docs = []

    # 1. Controller Header
    docs.append(f'''--- !u!91 &9100000
AnimatorController:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: {controller_name}
  serializedVersion: 5
  m_AnimatorParameters:
  - m_Name: Speed
    m_Type: 1
    m_DefaultFloat: 0
    m_DefaultInt: 0
    m_DefaultBool: 0
    m_Controller: {{fileID: 9100000}}
  - m_Name: Character
    m_Type: 3
    m_DefaultFloat: 0
    m_DefaultInt: 0
    m_DefaultBool: 0
    m_Controller: {{fileID: 9100000}}
  - m_Name: IsGrounded
    m_Type: 4
    m_DefaultFloat: 0
    m_DefaultInt: 0
    m_DefaultBool: 1
    m_Controller: {{fileID: 9100000}}
  - m_Name: IsBlocking
    m_Type: 4
    m_DefaultFloat: 0
    m_DefaultInt: 0
    m_DefaultBool: 0
    m_Controller: {{fileID: 9100000}}
  - m_Name: Attack1
    m_Type: 9
    m_DefaultFloat: 0
    m_DefaultInt: 0
    m_DefaultBool: 0
    m_Controller: {{fileID: 9100000}}
  - m_Name: Attack2
    m_Type: 9
    m_DefaultFloat: 0
    m_DefaultInt: 0
    m_DefaultBool: 0
    m_Controller: {{fileID: 9100000}}
  - m_Name: Attack3
    m_Type: 9
    m_DefaultFloat: 0
    m_DefaultInt: 0
    m_DefaultBool: 0
    m_Controller: {{fileID: 9100000}}
  - m_Name: HeavyThrust
    m_Type: 9
    m_DefaultFloat: 0
    m_DefaultInt: 0
    m_DefaultBool: 0
    m_Controller: {{fileID: 9100000}}
  - m_Name: Block
    m_Type: 9
    m_DefaultFloat: 0
    m_DefaultInt: 0
    m_DefaultBool: 0
    m_Controller: {{fileID: 9100000}}
  - m_Name: BlockHit
    m_Type: 9
    m_DefaultFloat: 0
    m_DefaultInt: 0
    m_DefaultBool: 0
    m_Controller: {{fileID: 9100000}}
  - m_Name: ParrySuccess
    m_Type: 9
    m_DefaultFloat: 0
    m_DefaultInt: 0
    m_DefaultBool: 0
    m_Controller: {{fileID: 9100000}}
  - m_Name: Dodge
    m_Type: 9
    m_DefaultFloat: 0
    m_DefaultInt: 0
    m_DefaultBool: 0
    m_Controller: {{fileID: 9100000}}
  - m_Name: Jump
    m_Type: 9
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
    m_Controller: {{fileID: 9100000}}''')

    # 2. StateMachine
    docs.append(f'''--- !u!1107 &110700000
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
    m_Position: {{x: 450, y: -70, z: 0}}
  - serializedVersion: 1
    m_State: {{fileID: 110200003}}
    m_Position: {{x: 450, y: 70, z: 0}}
  - serializedVersion: 1
    m_State: {{fileID: 110200004}}
    m_Position: {{x: 0, y: -160, z: 0}}
  - serializedVersion: 1
    m_State: {{fileID: 110200005}}
    m_Position: {{x: 0, y: -90, z: 0}}
  - serializedVersion: 1
    m_State: {{fileID: 110200006}}
    m_Position: {{x: 0, y: -20, z: 0}}
  - serializedVersion: 1
    m_State: {{fileID: 110200007}}
    m_Position: {{x: 200, y: -100, z: 0}}
  - serializedVersion: 1
    m_State: {{fileID: 110200008}}
    m_Position: {{x: 200, y: -160, z: 0}}
  - serializedVersion: 1
    m_State: {{fileID: 110200009}}
    m_Position: {{x: 0, y: 50, z: 0}}
  - serializedVersion: 1
    m_State: {{fileID: 110200010}}
    m_Position: {{x: 0, y: 120, z: 0}}
  - serializedVersion: 1
    m_State: {{fileID: 110200011}}
    m_Position: {{x: 200, y: 120, z: 0}}
  - serializedVersion: 1
    m_State: {{fileID: 110200012}}
    m_Position: {{x: 200, y: 180, z: 0}}
  - serializedVersion: 1
    m_State: {{fileID: 110200020}}
    m_Position: {{x: 200, y: 300, z: 0}}
  - serializedVersion: 1
    m_State: {{fileID: 110200021}}
    m_Position: {{x: 450, y: 300, z: 0}}
  - serializedVersion: 1
    m_State: {{fileID: 110200022}}
    m_Position: {{x: 0, y: 300, z: 0}}
  m_ChildStateMachines: []
  m_AnyStateTransitions:
  - {{fileID: 110100023}}
  - {{fileID: 110100024}}
  - {{fileID: 110100025}}
  - {{fileID: 110100026}}
  - {{fileID: 110100027}}
  - {{fileID: 110100028}}
  - {{fileID: 110100029}}
  - {{fileID: 110100033}}
  m_EntryTransitions:
  - {{fileID: 110900001}}
  - {{fileID: 110900002}}
  m_StateMachineTransitions: {{}}
  m_StateMachineBehaviours: []
  m_AnyStatePosition: {{x: -250, y: 0, z: 0}}
  m_EntryPosition: {{x: 220, y: -70, z: 0}}
  m_ExitPosition: {{x: 800, y: 120, z: 0}}
  m_ParentStateMachinePosition: {{x: 800, y: 20, z: 0}}
  m_DefaultState: {{fileID: {default_state_id}}}''')

    # 3. Entry Transitions
    docs.append('''--- !u!1109 &110900001
AnimatorTransition:
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: 
  m_Conditions:
  - m_ConditionMode: 6
    m_ConditionEvent: Character
    m_EventTreshold: 0
  m_DstStateMachine: {fileID: 0}
  m_DstState: {fileID: 110200001}
  m_Solo: 0
  m_Mute: 0
  m_IsExit: 0
  serializedVersion: 1''')

    docs.append('''--- !u!1109 &110900002
AnimatorTransition:
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {fileID: 0}
  m_PrefabInstance: {fileID: 0}
  m_PrefabAsset: {fileID: 0}
  m_Name: 
  m_Conditions:
  - m_ConditionMode: 6
    m_ConditionEvent: Character
    m_EventTreshold: 1
  m_DstStateMachine: {fileID: 0}
  m_DstState: {fileID: 110200020}
  m_Solo: 0
  m_Mute: 0
  m_IsExit: 0
  serializedVersion: 1''')

    # 4. States definitions
    states_data = [
        # (id, name, motion_guid, speed, [trans_ids])
        (110200001, 'Idle', 'c2f328d94dbd1a74cbf9dae13af0694a', 1, [110100001, 110100002]),
        (110200002, 'Walk', '170e7d004b17b354eba5aa3f9c8f6294', 1, [110100003, 110100004]),
        (110200003, 'Run', '24b1284220086724f923e92cf4e7a91e', 1, [110100005, 110100006]),
        (110200004, 'Jump', '04dcd389f3a112b4da8ef566fa9aff71', 1, [110100007, 110100008]),
        (110200005, 'Dodge', '8fdfbecac9f748943ba97a6402d2c335', 1, [110100010]),
        (110200006, 'Attack1', '967866d660fdeda46b995b90d691af49', 1, [110100011, 110100012]),
        (110200007, 'Attack2', '4b0277db09abb6045b0e34fd0e070779', 1, [110100013, 110100014]),
        (110200008, 'Attack3', 'fee55a76d1dee3d4a8cbbfe3e5ba1d4f', 1, [110100015]),
        (110200009, 'HeavyThrust', '0c0a4b2b3a3a3a54bbb69867f8305839', 1, [110100016]),
        (110200010, 'BlockGuard', '4e63f100e07b63749b8556043082d827', 1, [110100017, 110100018, 110100019]),
        (110200011, 'BlockHit', 'b685dd28e62cf9d4f99d22b1bc6c87b5', 1, [110100021]),
        (110200012, 'ParrySuccess', '324726b05408ee047b585320212ffafb', 1, [110100022]),
        # Mook
        (110200020, 'Mook_Idle', '61aed9a79fa24fff85023e4ede092067', 1, [110100030]),
        (110200021, 'Mook_Walk', 'd9383dbd37944c768e8fb8ddfaee7c30', 1, [110100031]),
        (110200022, 'Mook_AttackA', 'c594ad2eae024c829d6cb105fceb68dc', 1, [110100032]),
    ]

    for sid, sname, sguid, sspeed, strans in states_data:
        trans_block = '\n'.join([f'  - {{fileID: {tid}}}' for tid in strans])
        doc = f'''--- !u!1102 &{sid}
AnimatorState:
  serializedVersion: 6
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: {sname}
  m_Speed: {sspeed}
  m_CycleOffset: 0
  m_Transitions:
{trans_block}
  m_StateMachineBehaviours: []
  m_Position: {{x: 50, y: 50, z: 0}}
  m_IKOnFeet: 0
  m_WriteDefaultValues: 1
  m_Mirror: 0
  m_SpeedParameterActive: 0
  m_MirrorParameterActive: 0
  m_CycleOffsetParameterActive: 0
  m_TimeParameterActive: 0
  m_Motion: {{fileID: 7400000, guid: {sguid}, type: 2}}
  m_Tag: 
  m_SpeedParameter: 
  m_MirrorParameter: 
  m_CycleOffsetParameter: 
  m_TimeParameter: '''
        docs.append(doc)

    # 5. Helper function for transitions
    def make_transition(tid, dst_id, conditions, exit_time=0, exit_val=0.75, duration=0.1, can_self=0):
        cond_lines = []
        if conditions:
            cond_lines.append('  m_Conditions:')
            for mode, event, thresh in conditions:
                cond_lines.append(f'  - m_ConditionMode: {mode}')
                cond_lines.append(f'    m_ConditionEvent: {event}')
                cond_lines.append(f'    m_EventTreshold: {thresh}')
        else:
            cond_lines.append('  m_Conditions: []')
        conditions_block = '\n'.join(cond_lines)

        return f'''--- !u!1101 &{tid}
AnimatorStateTransition:
  m_ObjectHideFlags: 1
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: 
{conditions_block}
  m_DstStateMachine: {{fileID: 0}}
  m_DstState: {{fileID: {dst_id}}}
  m_Solo: 0
  m_Mute: 0
  m_IsExit: 0
  serializedVersion: 3
  m_TransitionDuration: {duration}
  m_TransitionOffset: 0
  m_ExitTime: {exit_val}
  m_HasExitTime: {exit_time}
  m_HasFixedDuration: 1
  m_InterruptionSource: 0
  m_OrderedInterruption: 1
  m_CanTransitionToSelf: {can_self}'''

    # State Transitions:
    docs.append(make_transition(110100001, 110200002, [(3, 'Speed', 0.1), (4, 'Speed', 0.6)], exit_time=0, duration=0.1))
    docs.append(make_transition(110100002, 110200003, [(3, 'Speed', 0.6)], exit_time=0, duration=0.1))
    docs.append(make_transition(110100003, 110200001, [(4, 'Speed', 0.1)], exit_time=0, duration=0.1))
    docs.append(make_transition(110100004, 110200003, [(3, 'Speed', 0.6)], exit_time=0, duration=0.1))
    docs.append(make_transition(110100005, 110200001, [(4, 'Speed', 0.1)], exit_time=0, duration=0.1))
    docs.append(make_transition(110100006, 110200002, [(4, 'Speed', 0.6), (3, 'Speed', 0.1)], exit_time=0, duration=0.1))

    # Jump transitions (One with exit time, one instant on landing)
    docs.append(make_transition(110100007, 110200001, [], exit_time=1, exit_val=0.92, duration=0.1))
    docs.append(make_transition(110100008, 110200001, [(1, 'IsGrounded', 0)], exit_time=0, duration=0))

    # Dodge
    docs.append(make_transition(110100010, 110200001, [], exit_time=1, exit_val=0.90, duration=0.1))

    # Attacks
    docs.append(make_transition(110100011, 110200001, [], exit_time=1, exit_val=0.90, duration=0.1))
    docs.append(make_transition(110100012, 110200007, [(1, 'Attack2', 0)], exit_time=0, duration=0.05))
    docs.append(make_transition(110100013, 110200001, [], exit_time=1, exit_val=0.90, duration=0.1))
    docs.append(make_transition(110100014, 110200008, [(1, 'Attack3', 0)], exit_time=0, duration=0.05))
    docs.append(make_transition(110100015, 110200001, [], exit_time=1, exit_val=0.90, duration=0.1))

    # HeavyThrust
    docs.append(make_transition(110100016, 110200001, [], exit_time=1, exit_val=0.90, duration=0.1))

    # Block
    docs.append(make_transition(110100017, 110200001, [(2, 'IsBlocking', 0)], exit_time=0, duration=0.1))
    docs.append(make_transition(110100018, 110200011, [(1, 'BlockHit', 0)], exit_time=0, duration=0.05))
    docs.append(make_transition(110100019, 110200012, [(1, 'ParrySuccess', 0)], exit_time=0, duration=0.05))
    docs.append(make_transition(110100021, 110200010, [], exit_time=1, exit_val=0.85, duration=0.1))
    docs.append(make_transition(110100022, 110200001, [], exit_time=1, exit_val=0.85, duration=0.1))

    # AnyState Qingfeng
    docs.append(make_transition(110100023, 110200004, [(6, 'Character', 0), (1, 'Jump', 0)], exit_time=0, duration=0.05, can_self=0))
    docs.append(make_transition(110100024, 110200005, [(6, 'Character', 0), (1, 'Dodge', 0)], exit_time=0, duration=0.05, can_self=0))
    docs.append(make_transition(110100025, 110200006, [(6, 'Character', 0), (1, 'Attack1', 0)], exit_time=0, duration=0.05, can_self=0))
    docs.append(make_transition(110100026, 110200007, [(6, 'Character', 0), (1, 'Attack2', 0)], exit_time=0, duration=0.05, can_self=0))
    docs.append(make_transition(110100027, 110200008, [(6, 'Character', 0), (1, 'Attack3', 0)], exit_time=0, duration=0.05, can_self=0))
    docs.append(make_transition(110100028, 110200009, [(6, 'Character', 0), (1, 'HeavyThrust', 0)], exit_time=0, duration=0.05, can_self=0))
    docs.append(make_transition(110100029, 110200010, [(6, 'Character', 0), (1, 'Block', 0)], exit_time=0, duration=0.05, can_self=0))

    # Mook Transitions
    docs.append(make_transition(110100030, 110200021, [(3, 'Speed', 0.1)], exit_time=0, duration=0.1))
    docs.append(make_transition(110100031, 110200020, [(4, 'Speed', 0.1)], exit_time=0, duration=0.1))
    docs.append(make_transition(110100032, 110200020, [], exit_time=1, exit_val=0.90, duration=0.1))
    # AnyState Mook
    docs.append(make_transition(110100033, 110200022, [(6, 'Character', 1), (1, 'AttackA', 0)], exit_time=0, duration=0.05, can_self=0))

    # Assemble file
    header = '%YAML 1.1\n%TAG !u! tag:yousandi.cn,2023:\n'
    content = header + '\n'.join(docs) + '\n'
    return content.replace('\r\n', '\n').replace('\n', '\r\n')

if __name__ == '__main__':
    # Player controller starts at Idle (110200001)
    player_text = build_unified_controller_text(default_state_id=110200001, controller_name="PlayerIdle")
    p1 = 'New Tuanjie Project/Assets/Sprites/Player/Idle/PlayerIdle.controller'
    with open(p1, 'wb') as f:
        f.write(player_text.encode('utf-8'))
    print('Written Player controller:', len(player_text))

    # Mook controller starts at Mook_Idle (110200020)
    mook_text = build_unified_controller_text(default_state_id=110200020, controller_name="MookSwordsman")
    p2 = 'New Tuanjie Project/Assets/Sprites/Enemies/MookSwordsman/MookSwordsman.controller'
    with open(p2, 'wb') as f:
        f.write(mook_text.encode('utf-8'))
    print('Written Mook controller:', len(mook_text))
