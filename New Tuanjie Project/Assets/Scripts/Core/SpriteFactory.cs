using UnityEngine;

/// <summary>运行时生成灰盒精灵：1×1 白像素，靠缩放与染色出形。</summary>
public static class SpriteFactory
{
    static Sprite pixel;

    public static Sprite Pixel
    {
        get
        {
            if (pixel == null)
            {
                Texture2D tex = new Texture2D(4, 4, TextureFormat.RGBA32, false);
                Color32[] px = new Color32[16];
                for (int i = 0; i < px.Length; i++) px[i] = new Color32(255, 255, 255, 255);
                tex.SetPixels32(px);
                tex.filterMode = FilterMode.Point;
                tex.Apply();
                pixel = Sprite.Create(tex, new Rect(0, 0, 4, 4), new Vector2(0.5f, 0.5f), 4f);
            }
            return pixel;
        }
    }

    /// <summary>在 parent 下建一个染色方块，size 为世界单位尺寸。</summary>
    public static GameObject CreateBox(Transform parent, string name, Vector2 size, Color color, int sortingOrder)
    {
        GameObject go = new GameObject(name);
        if (parent != null) go.transform.SetParent(parent, false);
        SpriteRenderer sr = go.AddComponent<SpriteRenderer>();
        sr.sprite = Pixel;
        sr.color = color;
        sr.sortingOrder = sortingOrder;
        go.transform.localScale = new Vector3(size.x, size.y, 1f);
        return go;
    }
}
