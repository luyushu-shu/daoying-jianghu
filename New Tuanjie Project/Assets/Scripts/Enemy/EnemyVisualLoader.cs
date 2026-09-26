using UnityEngine;
#if UNITY_EDITOR
using UnityEditor;
#endif

/// <summary>运行时加载敌人（如杂兵刀手）的 AnimatorController。</summary>
public static class EnemyVisualLoader
{
    const string SwordsmanControllerPath = "Assets/Sprites/Enemies/MookSwordsman/MookSwordsman.controller";

    public static RuntimeAnimatorController LoadSwordsmanController()
    {
#if UNITY_EDITOR
        return AssetDatabase.LoadAssetAtPath<RuntimeAnimatorController>(SwordsmanControllerPath);
#else
        return Resources.Load<RuntimeAnimatorController>("MookSwordsman");
#endif
    }
}
