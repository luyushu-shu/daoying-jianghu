using UnityEngine;

/// <summary>
/// 按「实际水平移速 / 设计移速」缩放 Animator 播放速率，
/// 让支撑脚后移速度跟上角色平移，消除打滑/溜冰（Footskate）。
/// 待机时恢复 1×，避免 Idle 被带着加速。
/// </summary>
[RequireComponent(typeof(Animator))]
public class CharacterFootskateFix : MonoBehaviour
{
    const float WalkThreshold = 0.1f;
    const float MoveEpsilon = 0.01f;

    [Header("设计基准参数")]
    [SerializeField] float baseMoveSpeed = QingfengWalkStride.DesignMoveSpeed;
    [SerializeField] float baseAnimSpeed = 1f;

    Animator animator;
    CombatActor combat;
    Vector3 lastPos;

    void Awake()
    {
        animator = GetComponent<Animator>();
        combat = GetComponent<CombatActor>();
        lastPos = transform.position;
        if (baseMoveSpeed < 0.01f)
            baseMoveSpeed = QingfengWalkStride.DesignMoveSpeed;
    }

    void LateUpdate()
    {
        if (animator == null) return;

        float currentSpeed;
        if (combat != null && combat.body != null)
            currentSpeed = Mathf.Abs(combat.body.vel.x);
        else
        {
            float dt = Mathf.Max(Time.deltaTime, 1e-6f);
            currentSpeed = Mathf.Abs(transform.position.x - lastPos.x) / dt;
        }
        lastPos = transform.position;

        bool walking = false;
        if (animator.runtimeAnimatorController != null)
            walking = animator.GetFloat("Speed") > WalkThreshold;

        if (walking && currentSpeed > MoveEpsilon)
            animator.speed = (currentSpeed / baseMoveSpeed) * baseAnimSpeed;
        else
            animator.speed = baseAnimSpeed;
    }
}
