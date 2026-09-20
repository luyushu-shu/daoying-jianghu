using UnityEngine;

/// <summary>横版跟随镜头：主角偏前向三分之一，带震屏偏移与场地边界。</summary>
public class SimpleCameraFollow : MonoBehaviour
{
    public Transform target;
    public Vector2 min = new Vector2(-17f, 0.5f);
    public Vector2 max = new Vector2(17f, 8f);
    public float smooth = 6f;

    Vector3 vel;

    void LateUpdate()
    {
        if (target == null) return;
        float lookAhead = 0f;
        CombatActor a = target.GetComponent<CombatActor>();
        if (a != null) lookAhead = a.facing * 1.5f;

        Vector3 want = target.position + new Vector3(lookAhead, 1.6f, -10f);
        want.x = Mathf.Clamp(want.x, min.x, max.x);
        want.y = Mathf.Clamp(want.y, min.y, max.y);

        Vector3 p = Vector3.SmoothDamp(transform.position, want, ref vel, 1f / smooth);
        if (CombatDirector.Instance != null)
        {
            Vector2 sh = CombatDirector.Instance.ShakeOffset;
            p.x += sh.x; p.y += sh.y;
        }
        p.z = -10f;
        transform.position = p;
    }
}
