using UnityEngine;
#if UNITY_EDITOR
using UnityEditor;
#endif

/// <summary>运行时加载玩家待机/行走 AnimatorController。</summary>
public static class PlayerVisualLoader
{
    const string ControllerPath = "Assets/Sprites/Player/Idle/PlayerIdle.controller";

    public static RuntimeAnimatorController LoadController()
    {
#if UNITY_EDITOR
        return AssetDatabase.LoadAssetAtPath<RuntimeAnimatorController>(ControllerPath);
#else
        return Resources.Load<RuntimeAnimatorController>("PlayerIdle");
#endif
    }
}
