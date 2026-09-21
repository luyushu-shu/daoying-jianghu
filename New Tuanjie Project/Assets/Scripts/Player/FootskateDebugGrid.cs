using UnityEngine;

/// <summary>地面刻度线：逐帧对照支撑脚是否锁在同一根线上。</summary>
public static class FootskateDebugGrid
{
    const string RootName = "FootskateGrid";

    public static void SpawnIfMissing()
    {
        if (GameObject.Find(RootName) != null) return;

        GameObject root = new GameObject(RootName);
        float spacing = 0.25f;
        int count = 80;
        float origin = -count * 0.5f * spacing;
        for (int i = 0; i <= count; i++)
        {
            float x = origin + i * spacing;
            bool major = i % 4 == 0;
            float h = major ? 0.22f : 0.1f;
            Color c = major
                ? new Color(0.85f, 0.2f, 0.2f, 0.55f)
                : new Color(0.55f, 0.55f, 0.6f, 0.35f);
            GameObject tick = SpriteFactory.CreateBox(root.transform, "tick", new Vector2(0.02f, h), c, -2);
            tick.transform.position = new Vector3(x, h * 0.5f, 1f);
        }

        GameObject ground = SpriteFactory.CreateBox(root.transform, "ground", new Vector2(count * spacing + 1f, 0.02f),
            new Color(0.7f, 0.25f, 0.25f, 0.5f), -3);
        ground.transform.position = new Vector3(0f, 0f, 1f);
    }
}
