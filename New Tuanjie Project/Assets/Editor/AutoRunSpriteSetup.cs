using System;
using System.IO;
using UnityEditor;
using UnityEngine;

/// <summary>
/// 一次性自执行器：检测到 Assets/_run_sprite_setup.marker 存在时，
/// 在当前打开的编辑器里自动调用 SpriteAnimSetup.Setup()，并写出结果标记文件。
/// rev: 12 待机 8 帧、奔跑 9 帧，轴心改到脚底
/// </summary>
[InitializeOnLoad]
public static class AutoRunSpriteSetup
{
    static AutoRunSpriteSetup()
    {
        string marker = "Assets/_run_sprite_setup.marker";
        if (!File.Exists(marker)) return;
        try { File.Delete(marker); } catch { /* 忽略 */ }
        EditorApplication.delayCall += () =>
        {
            string result = "OK";
            try
            {
                SpriteAnimSetup.Setup();
            }
            catch (Exception e)
            {
                result = "FAIL: " + e.Message + "\n" + e.StackTrace;
                Debug.LogException(e);
            }
            try { File.WriteAllText("Assets/_sprite_setup_done.txt", result); } catch { /* 忽略 */ }
        };
    }
}
