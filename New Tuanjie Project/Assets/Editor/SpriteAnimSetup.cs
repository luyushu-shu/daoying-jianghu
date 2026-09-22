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
    const string ControllerPath = IdleDir + "/PlayerIdle.controller";
    const string IdleClipPath = IdleDir + "/PlayerIdle.anim";
    const string WalkClipPath = WalkDir + "/PlayerWalk.anim";
    const string RunClipPath = RunDir + "/PlayerRun.anim";
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
    const float IdleFrameSeconds = 0.16f;
    const float WalkFrameSeconds = 0.14f;
    const float RunFrameSeconds = QingfengRunStride.FrameSeconds;
    const float RunSpeedThreshold = 0.55f;
    static readonly Vector2 FeetPivot = new Vector2(0.5f, 0.09f);

    [MenuItem("刀影江湖/生成待机行走奔跑帧动画")]
    public static void Setup()
    {
        Sprite[] idleSprites = ImportFrames(IdleDir, IdleFrames, 214f);
        if (idleSprites == null) return;
        Sprite[] walkSprites = ImportFrames(WalkDir, WalkFrames, 100f);
        if (walkSprites == null) return;
        Sprite[] runSprites = ImportFrames(RunDir, RunFrames, 214f);
        if (runSprites == null) return;

        AnimationClip idleClip = WriteLoopClip(IdleClipPath, "PlayerIdle", idleSprites, IdleFrameSeconds);
        AnimationClip walkClip = WriteLoopClip(WalkClipPath, "PlayerWalk", walkSprites, WalkFrameSeconds);
        AnimationClip runClip = WriteLoopClip(RunClipPath, "PlayerRun", runSprites, RunFrameSeconds);

        AnimatorController controller = AssetDatabase.LoadAssetAtPath<AnimatorController>(ControllerPath);
        if (controller == null)
            controller = AnimatorController.CreateAnimatorControllerAtPath(ControllerPath);
        RebuildLocomotionController(controller, idleClip, walkClip, runClip);
        EditorUtility.SetDirty(controller);

        BindPreviewCharacter(controller, idleSprites[0]);

        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        Debug.Log("[SpriteAnimSetup] 完成：Idle/Walk/Run，Speed 衔接。预览 A/D 走，Shift+A/D 跑。");
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

    static AnimationClip WriteLoopClip(string path, string name, Sprite[] sprites, float frameSeconds)
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
        settings.loopTime = true;
        AnimationUtility.SetAnimationClipSettings(clip, settings);

        if (created)
            AssetDatabase.CreateAsset(clip, path);
        else
            EditorUtility.SetDirty(clip);
        return clip;
    }

    static void RebuildLocomotionController(AnimatorController controller, AnimationClip idle, AnimationClip walk, AnimationClip run)
    {
        for (int i = controller.parameters.Length - 1; i >= 0; i--)
            controller.RemoveParameter(i);
        controller.AddParameter("Speed", AnimatorControllerParameterType.Float);

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
        sm.defaultState = idleState;

        AddSpeedTransition(idleState, walkState, AnimatorConditionMode.Greater, 0.1f);
        AddSpeedTransition(idleState, runState, AnimatorConditionMode.Greater, RunSpeedThreshold);
        AddSpeedTransition(walkState, runState, AnimatorConditionMode.Greater, RunSpeedThreshold);
        AddSpeedTransition(walkState, idleState, AnimatorConditionMode.Less, 0.1f);
        AddSpeedTransition(runState, walkState, AnimatorConditionMode.Less, RunSpeedThreshold);
        AddSpeedTransition(runState, idleState, AnimatorConditionMode.Less, 0.1f);
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
        if (go.GetComponent<PlayerSpriteLocomotion>() == null)
            go.AddComponent<PlayerSpriteLocomotion>();
        if (go.GetComponent<CharacterFootskateFix>() == null)
            go.AddComponent<CharacterFootskateFix>();
        FootskateDebugGrid.SpawnIfMissing();

        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene, PreviewScenePath);
    }
}
