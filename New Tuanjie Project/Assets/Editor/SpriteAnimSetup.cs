using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// 把待机 / 行走 / 奔跑帧导入为精灵，写成循环 AnimationClip，
/// 并在 PlayerIdle.controller 里用 Speed 衔接 Idle ↔ Walk ↔ Run。
/// 批处理：Tuanjie.exe -batchmode -quit -projectPath &lt;proj&gt; -executeMethod SpriteAnimSetup.Setup
/// </summary>
public static class SpriteAnimSetup
{
    const string IdleDir = "Assets/Sprites/Player/Idle";
    const string WalkDir = "Assets/Sprites/Player/Walk";
    const string RunDir = "Assets/Sprites/Player/Run";
    const string DodgeDir = "Assets/Sprites/Player/Dodge";
    const string AttackDir = "Assets/Sprites/Player/Attack";
    const string JumpDir = "Assets/Sprites/Player/Jump";
    const string HeavyThrustDir = "Assets/Sprites/Player/HeavyThrust";
    const string BlockGuardDir = "Assets/Sprites/Player/Block/Guard";
    const string BlockHitDir = "Assets/Sprites/Player/Block/Hit";
    const string BlockParryDir = "Assets/Sprites/Player/Block/Parry";
    const string ControllerPath = IdleDir + "/PlayerIdle.controller";
    const string IdleClipPath = IdleDir + "/PlayerIdle.anim";
    const string WalkClipPath = WalkDir + "/PlayerWalk.anim";
    const string RunClipPath = RunDir + "/PlayerRun.anim";
    const string DodgeClipPath = DodgeDir + "/PlayerDodge.anim";
    const string Attack1ClipPath = AttackDir + "/PlayerAttack1.anim";
    const string Attack2ClipPath = AttackDir + "/PlayerAttack2.anim";
    const string Attack3ClipPath = AttackDir + "/PlayerAttack3.anim";
    const string JumpClipPath = JumpDir + "/PlayerJump.anim";
    const string HeavyThrustClipPath = HeavyThrustDir + "/PlayerHeavyThrust.anim";
    const string BlockGuardClipPath = "Assets/Sprites/Player/Block/PlayerBlockGuard.anim";
    const string BlockHitClipPath = "Assets/Sprites/Player/Block/PlayerBlockHit.anim";
    const string BlockParryClipPath = "Assets/Sprites/Player/Block/PlayerParrySuccess.anim";
    const string BlockClipPath = "Assets/Sprites/Player/Block/PlayerBlock.anim";
    const string PreviewScenePath = "Assets/Scenes/SpritePreview.unity";
    static readonly string[] IdleFrames =
    {
        "idle-1", "idle-2", "idle-3", "idle-4",
        "idle-5", "idle-6", "idle-7", "idle-8"
    };
    static readonly string[] WalkFrames =
    {
        "walk-1", "walk-2", "walk-3", "walk-4", "walk-5",
        "walk-6", "walk-7", "walk-8", "walk-9", "walk-10",
        "walk-11", "walk-12", "walk-13", "walk-14", "walk-15"
    };
    static readonly string[] RunFrames =
    {
        "run-1", "run-2", "run-3", "run-4", "run-5",
        "run-6", "run-7", "run-8", "run-9"
    };
    static readonly string[] DodgeFrames =
    {
        "dodge-1", "dodge-2", "dodge-3", "dodge-4",
        "dodge-5", "dodge-6", "dodge-7", "dodge-8"
    };
    static readonly string[] Attack1Frames =
    {
        "attack-1", "attack-2", "attack-3", "attack-4"
    };
    static readonly string[] Attack2Frames =
    {
        "attack-5", "attack-6", "attack-7", "attack-8"
    };
    static readonly string[] Attack3Frames =
    {
        "attack-9", "attack-10", "attack-11", "attack-12"
    };
    static readonly string[] JumpFrames =
    {
        "jump-1", "jump-2", "jump-3", "jump-4",
        "jump-5", "jump-6", "jump-7", "jump-8"
    };
    static readonly string[] HeavyThrustFrames =
    {
        "heavy-1", "heavy-2", "heavy-3", "heavy-4",
        "heavy-5", "heavy-6", "heavy-7", "heavy-8"
    };
    static readonly string[] BlockGuardFrames =
    {
        "guard-1", "guard-2", "guard-3", "guard-4",
        "guard-5", "guard-6", "guard-7"
    };
    static readonly string[] BlockHitFrames =
    {
        "hit-1", "hit-2", "hit-3", "hit-4"
    };
    static readonly string[] BlockParryFrames =
    {
        "parry-1", "parry-2", "parry-3", "parry-4",
        "parry-5", "parry-6"
    };
    const float IdleFrameSeconds = 0.16f;
    const float WalkFrameSeconds = 0.14f;
    const float RunFrameSeconds = QingfengRunStride.FrameSeconds;
    const float DodgeFrameSeconds = 0.075f;
    const float AttackFrameSeconds = 0.085f;
    const float JumpFrameSeconds = 0.085f;
    const float HeavyThrustFrameSeconds = 0.095f;
    const float BlockGuardFrameSeconds = 0.085f;
    const float BlockHitFrameSeconds = 0.075f;
    const float BlockParryFrameSeconds = 0.085f;
    const float RunSpeedThreshold = 0.55f;
    static readonly Vector2 FeetPivot = new Vector2(0.5f, 0.09f);

    [MenuItem("刀影江湖/生成待机行走奔跑闪避攻击跳跃重刺格挡帧动画")]
    public static void Setup()
    {
        Sprite[] idleSprites = ImportFrames(IdleDir, IdleFrames, 214f);
        if (idleSprites == null) return;
        Sprite[] walkSprites = ImportFrames(WalkDir, WalkFrames, 100f);
        if (walkSprites == null) return;
        Sprite[] runSprites = ImportFrames(RunDir, RunFrames, 214f);
        if (runSprites == null) return;
        Sprite[] dodgeSprites = ImportFrames(DodgeDir, DodgeFrames, 214f);
        if (dodgeSprites == null) return;
        Sprite[] atk1Sprites = ImportFrames(AttackDir, Attack1Frames, 214f);
        if (atk1Sprites == null) return;
        Sprite[] atk2Sprites = ImportFrames(AttackDir, Attack2Frames, 214f);
        if (atk2Sprites == null) return;
        Sprite[] atk3Sprites = ImportFrames(AttackDir, Attack3Frames, 214f);
        if (atk3Sprites == null) return;
        Sprite[] jumpSprites = ImportFrames(JumpDir, JumpFrames, 214f);
        if (jumpSprites == null) return;
        Sprite[] heavySprites = ImportFrames(HeavyThrustDir, HeavyThrustFrames, 214f);
        if (heavySprites == null) return;
        Sprite[] guardSprites = ImportFrames(BlockGuardDir, BlockGuardFrames, 214f);
        if (guardSprites == null) return;
        Sprite[] hitSprites = ImportFrames(BlockHitDir, BlockHitFrames, 214f);
        if (hitSprites == null) return;
        Sprite[] parrySprites = ImportFrames(BlockParryDir, BlockParryFrames, 214f);
        if (parrySprites == null) return;

        AnimationClip idleClip = WriteClip(IdleClipPath, "PlayerIdle", idleSprites, IdleFrameSeconds, true);
        AnimationClip walkClip = WriteClip(WalkClipPath, "PlayerWalk", walkSprites, WalkFrameSeconds, true);
        AnimationClip runClip = WriteClip(RunClipPath, "PlayerRun", runSprites, RunFrameSeconds, true);
        AnimationClip dodgeClip = WriteClip(DodgeClipPath, "PlayerDodge", dodgeSprites, DodgeFrameSeconds, false);
        AnimationClip atk1Clip = WriteClip(Attack1ClipPath, "PlayerAttack1", atk1Sprites, AttackFrameSeconds, false);
        AnimationClip atk2Clip = WriteClip(Attack2ClipPath, "PlayerAttack2", atk2Sprites, AttackFrameSeconds, false);
        AnimationClip atk3Clip = WriteClip(Attack3ClipPath, "PlayerAttack3", atk3Sprites, AttackFrameSeconds, false);
        AnimationClip jumpClip = WriteClip(JumpClipPath, "PlayerJump", jumpSprites, JumpFrameSeconds, false);
        AnimationClip heavyClip = WriteClip(HeavyThrustClipPath, "PlayerHeavyThrust", heavySprites, HeavyThrustFrameSeconds, false);
        AnimationClip blockGuardClip = WriteClip(BlockGuardClipPath, "PlayerBlockGuard", guardSprites, BlockGuardFrameSeconds, false);
        AnimationClip blockHitClip = WriteClip(BlockHitClipPath, "PlayerBlockHit", hitSprites, BlockHitFrameSeconds, false);
        AnimationClip blockParryClip = WriteClip(BlockParryClipPath, "PlayerParrySuccess", parrySprites, BlockParryFrameSeconds, false);
        WriteClip(BlockClipPath, "PlayerBlock", guardSprites, BlockGuardFrameSeconds, false);

        AnimatorController controller = AssetDatabase.LoadAssetAtPath<AnimatorController>(ControllerPath);
        if (controller == null)
            controller = AnimatorController.CreateAnimatorControllerAtPath(ControllerPath);
        RebuildLocomotionController(controller, idleClip, walkClip, runClip, dodgeClip, atk1Clip, atk2Clip, atk3Clip, jumpClip, heavyClip, blockGuardClip, blockHitClip, blockParryClip);
        EditorUtility.SetDirty(controller);

        BindPreviewCharacter(controller, idleSprites[0]);

        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        Debug.Log("[SpriteAnimSetup] 完成：三种格挡（没挡刀纯姿势/普通格挡微光/完美格挡大特效）及全套动作已编译更新！F:空放格挡, G:普通格挡微光, T:完美格挡大特效。");
    }

    static Sprite[] ImportFrames(string dir, string[] names, float pixelsPerUnit)
    {
        Sprite[] sprites = new Sprite[names.Length];
        for (int i = 0; i < names.Length; i++)
        {
            string path = dir + "/" + names[i] + ".png";
            TextureImporter ti = AssetImporter.GetAtPath(path) as TextureImporter;
            if (ti == null)
            {
                Debug.LogError("[SpriteAnimSetup] 找不到贴图 " + path);
                return null;
            }
            ti.textureType = TextureImporterType.Sprite;
            ti.spriteImportMode = SpriteImportMode.Single;
            TextureImporterSettings texSettings = new TextureImporterSettings();
            ti.ReadTextureSettings(texSettings);
            texSettings.spriteAlignment = (int)SpriteAlignment.Custom;
            texSettings.spritePivot = FeetPivot;
            texSettings.spritePixelsPerUnit = pixelsPerUnit;
            ti.SetTextureSettings(texSettings);
            ti.spritePivot = FeetPivot;
            ti.spritePixelsPerUnit = pixelsPerUnit;
            ti.filterMode = FilterMode.Bilinear;
            ti.mipmapEnabled = false;
            ti.alphaIsTransparency = true;
            ti.SaveAndReimport();
            sprites[i] = AssetDatabase.LoadAssetAtPath<Sprite>(path);
            if (sprites[i] == null)
            {
                Debug.LogError("[SpriteAnimSetup] 精灵加载失败 " + path);
                return null;
            }
        }
        return sprites;
    }

    static AnimationClip WriteClip(string path, string name, Sprite[] sprites, float frameSeconds, bool loop)
    {
        AnimationClip clip = AssetDatabase.LoadAssetAtPath<AnimationClip>(path);
        bool created = false;
        if (clip == null)
        {
            clip = new AnimationClip();
            created = true;
        }

        clip.name = name;
        clip.frameRate = Mathf.Max(1f, 1f / frameSeconds);
        EditorCurveBinding binding = EditorCurveBinding.PPtrCurve("", typeof(SpriteRenderer), "m_Sprite");
        ObjectReferenceKeyframe[] keys = new ObjectReferenceKeyframe[sprites.Length];
        for (int i = 0; i < sprites.Length; i++)
            keys[i] = new ObjectReferenceKeyframe { time = i * frameSeconds, value = sprites[i] };
        AnimationUtility.SetObjectReferenceCurve(clip, binding, keys);
        AnimationClipSettings settings = AnimationUtility.GetAnimationClipSettings(clip);
        settings.loopTime = loop;
        AnimationUtility.SetAnimationClipSettings(clip, settings);

        if (created)
            AssetDatabase.CreateAsset(clip, path);
        else
            EditorUtility.SetDirty(clip);
        return clip;
    }

    static void RebuildLocomotionController(AnimatorController controller, AnimationClip idle, AnimationClip walk, AnimationClip run, AnimationClip dodge, AnimationClip atk1, AnimationClip atk2, AnimationClip atk3, AnimationClip jump, AnimationClip heavy, AnimationClip blockGuard, AnimationClip blockHit, AnimationClip parrySuccess)
    {
        for (int i = controller.parameters.Length - 1; i >= 0; i--)
            controller.RemoveParameter(i);
        controller.AddParameter("Speed", AnimatorControllerParameterType.Float);
        controller.AddParameter("Dodge", AnimatorControllerParameterType.Trigger);
        controller.AddParameter("Attack1", AnimatorControllerParameterType.Trigger);
        controller.AddParameter("Attack2", AnimatorControllerParameterType.Trigger);
        controller.AddParameter("Attack3", AnimatorControllerParameterType.Trigger);
        controller.AddParameter("Jump", AnimatorControllerParameterType.Trigger);
        controller.AddParameter("HeavyThrust", AnimatorControllerParameterType.Trigger);
        controller.AddParameter("Block", AnimatorControllerParameterType.Trigger);
        controller.AddParameter("BlockHit", AnimatorControllerParameterType.Trigger);
        controller.AddParameter("ParrySuccess", AnimatorControllerParameterType.Trigger);
        controller.AddParameter("IsGrounded", AnimatorControllerParameterType.Bool);

        AnimatorStateMachine sm = controller.layers[0].stateMachine;
        ChildAnimatorState[] existing = sm.states;
        for (int i = 0; i < existing.Length; i++)
            sm.RemoveState(existing[i].state);

        AnimatorState idleState = sm.AddState("Idle", new Vector3(200f, 0f, 0f));
        idleState.motion = idle;
        AnimatorState walkState = sm.AddState("Walk", new Vector3(480f, 0f, 0f));
        walkState.motion = walk;
        AnimatorState runState = sm.AddState("Run", new Vector3(760f, 0f, 0f));
        runState.motion = run;
        AnimatorState dodgeState = sm.AddState("Dodge", new Vector3(480f, -120f, 0f));
        dodgeState.motion = dodge;
        AnimatorState jumpState = sm.AddState("Jump", new Vector3(200f, -120f, 0f));
        jumpState.motion = jump;

        AnimatorState atk1State = sm.AddState("Attack1", new Vector3(200f, 140f, 0f));
        atk1State.motion = atk1;
        AnimatorState atk2State = sm.AddState("Attack2", new Vector3(480f, 140f, 0f));
        atk2State.motion = atk2;
        AnimatorState atk3State = sm.AddState("Attack3", new Vector3(760f, 140f, 0f));
        atk3State.motion = atk3;
        AnimatorState heavyState = sm.AddState("HeavyThrust", new Vector3(480f, 260f, 0f));
        heavyState.motion = heavy;

        // 三种格挡状态
        AnimatorState blockGuardState = sm.AddState("BlockGuard", new Vector3(200f, 260f, 0f));
        blockGuardState.motion = blockGuard;
        AnimatorState blockHitState = sm.AddState("BlockHit", new Vector3(480f, 380f, 0f));
        blockHitState.motion = blockHit;
        AnimatorState parrySuccessState = sm.AddState("ParrySuccess", new Vector3(200f, 380f, 0f));
        parrySuccessState.motion = parrySuccess;

        sm.defaultState = idleState;

        AddSpeedTransition(idleState, walkState, AnimatorConditionMode.Greater, 0.1f);
        AddSpeedTransition(idleState, runState, AnimatorConditionMode.Greater, RunSpeedThreshold);
        AddSpeedTransition(walkState, runState, AnimatorConditionMode.Greater, RunSpeedThreshold);
        AddSpeedTransition(walkState, idleState, AnimatorConditionMode.Less, 0.1f);
        AddSpeedTransition(runState, walkState, AnimatorConditionMode.Less, RunSpeedThreshold);
        AddSpeedTransition(runState, idleState, AnimatorConditionMode.Less, 0.1f);

        // AnyState -> Dodge
        AnimatorStateTransition toDodge = sm.AddAnyStateTransition(dodgeState);
        toDodge.hasExitTime = false;
        toDodge.hasFixedDuration = true;
        toDodge.duration = 0.02f;
        toDodge.AddCondition(AnimatorConditionMode.If, 0f, "Dodge");

        // AnyState -> Jump
        AnimatorStateTransition toJump = sm.AddAnyStateTransition(jumpState);
        toJump.hasExitTime = false;
        toJump.hasFixedDuration = true;
        toJump.duration = 0.02f;
        toJump.AddCondition(AnimatorConditionMode.If, 0f, "Jump");

        // AnyState -> HeavyThrust
        AnimatorStateTransition toHeavy = sm.AddAnyStateTransition(heavyState);
        toHeavy.hasExitTime = false;
        toHeavy.hasFixedDuration = true;
        toHeavy.duration = 0.02f;
        toHeavy.AddCondition(AnimatorConditionMode.If, 0f, "HeavyThrust");

        // AnyState -> BlockGuard (没挡刀，纯姿势)
        AnimatorStateTransition toGuard = sm.AddAnyStateTransition(blockGuardState);
        toGuard.hasExitTime = false;
        toGuard.hasFixedDuration = true;
        toGuard.duration = 0.02f;
        toGuard.AddCondition(AnimatorConditionMode.If, 0f, "Block");

        // AnyState -> BlockHit (普通格挡成功，微弱亮光)
        AnimatorStateTransition toHit = sm.AddAnyStateTransition(blockHitState);
        toHit.hasExitTime = false;
        toHit.hasFixedDuration = true;
        toHit.duration = 0.02f;
        toHit.AddCondition(AnimatorConditionMode.If, 0f, "BlockHit");

        // AnyState -> ParrySuccess (完美格挡成功，暴烈大特效)
        AnimatorStateTransition toParry = sm.AddAnyStateTransition(parrySuccessState);
        toParry.hasExitTime = false;
        toParry.hasFixedDuration = true;
        toParry.duration = 0.02f;
        toParry.AddCondition(AnimatorConditionMode.If, 0f, "ParrySuccess");

        // AnyState -> Attack1
        AnimatorStateTransition toAtk1 = sm.AddAnyStateTransition(atk1State);
        toAtk1.hasExitTime = false;
        toAtk1.hasFixedDuration = true;
        toAtk1.duration = 0.02f;
        toAtk1.AddCondition(AnimatorConditionMode.If, 0f, "Attack1");

        // AnyState -> Attack2
        AnimatorStateTransition toAtk2 = sm.AddAnyStateTransition(atk2State);
        toAtk2.hasExitTime = false;
        toAtk2.hasFixedDuration = true;
        toAtk2.duration = 0.02f;
        toAtk2.AddCondition(AnimatorConditionMode.If, 0f, "Attack2");

        // AnyState -> Attack3
        AnimatorStateTransition toAtk3 = sm.AddAnyStateTransition(atk3State);
        toAtk3.hasExitTime = false;
        toAtk3.hasFixedDuration = true;
        toAtk3.duration = 0.02f;
        toAtk3.AddCondition(AnimatorConditionMode.If, 0f, "Attack3");

        // HeavyThrust -> Idle
        AnimatorStateTransition fromHeavy = heavyState.AddTransition(idleState);
        fromHeavy.hasExitTime = true;
        fromHeavy.exitTime = 0.92f;
        fromHeavy.hasFixedDuration = true;
        fromHeavy.duration = 0.05f;

        // BlockGuard -> Idle
        AnimatorStateTransition fromGuard = blockGuardState.AddTransition(idleState);
        fromGuard.hasExitTime = true;
        fromGuard.exitTime = 0.92f;
        fromGuard.hasFixedDuration = true;
        fromGuard.duration = 0.05f;

        // BlockHit -> Idle
        AnimatorStateTransition fromHit = blockHitState.AddTransition(idleState);
        fromHit.hasExitTime = true;
        fromHit.exitTime = 0.90f;
        fromHit.hasFixedDuration = true;
        fromHit.duration = 0.05f;

        // ParrySuccess -> Idle
        AnimatorStateTransition fromParry = parrySuccessState.AddTransition(idleState);
        fromParry.hasExitTime = true;
        fromParry.exitTime = 0.92f;
        fromParry.hasFixedDuration = true;
        fromParry.duration = 0.05f;

        // Jump -> Idle (落地回正)
        AnimatorStateTransition fromJump = jumpState.AddTransition(idleState);
        fromJump.hasExitTime = true;
        fromJump.exitTime = 0.92f;
        fromJump.hasFixedDuration = true;
        fromJump.duration = 0.05f;

        // Dodge -> Idle
        AnimatorStateTransition fromDodge = dodgeState.AddTransition(idleState);
        fromDodge.hasExitTime = true;
        fromDodge.exitTime = 0.95f;
        fromDodge.hasFixedDuration = true;
        fromDodge.duration = 0.05f;

        // Attack1 -> Idle
        AnimatorStateTransition fromAtk1 = atk1State.AddTransition(idleState);
        fromAtk1.hasExitTime = true;
        fromAtk1.exitTime = 0.92f;
        fromAtk1.hasFixedDuration = true;
        fromAtk1.duration = 0.05f;

        // Attack2 -> Idle
        AnimatorStateTransition fromAtk2 = atk2State.AddTransition(idleState);
        fromAtk2.hasExitTime = true;
        fromAtk2.exitTime = 0.92f;
        fromAtk2.hasFixedDuration = true;
        fromAtk2.duration = 0.05f;

        // Attack3 -> Idle
        AnimatorStateTransition fromAtk3 = atk3State.AddTransition(idleState);
        fromAtk3.hasExitTime = true;
        fromAtk3.exitTime = 0.92f;
        fromAtk3.hasFixedDuration = true;
        fromAtk3.duration = 0.05f;
    }

    static void AddSpeedTransition(AnimatorState from, AnimatorState to, AnimatorConditionMode mode, float threshold)
    {
        AnimatorStateTransition t = from.AddTransition(to);
        t.hasExitTime = false;
        t.hasFixedDuration = true;
        t.duration = 0f;
        t.AddCondition(mode, threshold, "Speed");
    }

    static void BindPreviewCharacter(AnimatorController controller, Sprite idleSprite)
    {
        if (EditorApplication.isPlaying)
        {
            GameObject liveGo = GameObject.Find("QingfengIdle");
            if (liveGo != null)
            {
                Animator anim = liveGo.GetComponent<Animator>();
                if (anim != null) anim.runtimeAnimatorController = controller;
            }
            return;
        }

        Scene scene;
        if (System.IO.File.Exists(PreviewScenePath))
            scene = EditorSceneManager.OpenScene(PreviewScenePath, OpenSceneMode.Single);
        else
            scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

        GameObject go = GameObject.Find("QingfengIdle");
        if (go == null)
        {
            go = new GameObject("QingfengIdle");
            go.AddComponent<SpriteRenderer>();
            go.AddComponent<Animator>();
        }

        SpriteRenderer sr = go.GetComponent<SpriteRenderer>();
        sr.sprite = idleSprite;
        Animator animator = go.GetComponent<Animator>();
        animator.runtimeAnimatorController = controller;
        if (go.GetComponent<CharacterFootskateFix>() == null)
            go.AddComponent<CharacterFootskateFix>();
        FootskateDebugGrid.SpawnIfMissing();

        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene, PreviewScenePath);
    }
}
