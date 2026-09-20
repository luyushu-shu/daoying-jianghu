using UnityEngine;

/// <summary>
/// 运动学角色体：不用碰撞体，靠 BoxCast 对 Ground 层做移动解算。
/// pos 为脚底中心。帧级手感要求位移完全确定，故不走物理碰撞。
/// </summary>
public class KinematicBody2D
{
    public const int GroundMask = 1 << 6;

    public Vector2 pos;
    public Vector2 vel;
    public bool grounded;
    public readonly Vector2 size = new Vector2(0.7f, 1.4f); // 宽×高（1身=1.4单位）

    const float Skin = 0.02f;

    public Vector2 Center { get { return pos + new Vector2(0f, size.y * 0.5f); } }

    public void Simulate(float dt)
    {
        // 水平
        float dx = vel.x * dt;
        if (Mathf.Abs(dx) > 0.00001f)
        {
            Vector2 dir = new Vector2(Mathf.Sign(dx), 0f);
            RaycastHit2D hit = Physics2D.BoxCast(Center, size * 0.9f, 0f, dir, Mathf.Abs(dx) + Skin, GroundMask);
            if (hit.collider != null)
            {
                dx = Mathf.Sign(dx) * Mathf.Max(0f, hit.distance - Skin);
                vel.x = 0f;
            }
            pos.x += dx;
        }

        // 垂直
        float dy = vel.y * dt;
        grounded = false;
        if (dy <= 0f)
        {
            RaycastHit2D hit = Physics2D.BoxCast(Center, size * 0.9f, 0f, Vector2.down, -dy + 0.06f, GroundMask);
            if (hit.collider != null)
            {
                pos.y = hit.point.y + 0.001f;
                vel.y = 0f;
                grounded = true;
            }
            else pos.y += dy;
        }
        else
        {
            RaycastHit2D hit = Physics2D.BoxCast(Center, size * 0.9f, 0f, Vector2.up, dy + Skin, GroundMask);
            if (hit.collider != null)
            {
                pos.y += Mathf.Sign(dy) * Mathf.Max(0f, hit.distance - Skin);
                vel.y = 0f;
            }
            else pos.y += dy;
        }
    }

    /// <summary>静止时探测脚下是否仍有地。</summary>
    public bool CheckGround()
    {
        return Physics2D.BoxCast(Center, size * 0.9f, 0f, Vector2.down, 0.08f, GroundMask).collider != null;
    }
}
