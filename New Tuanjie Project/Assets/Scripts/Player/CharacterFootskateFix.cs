using UnityEngine;

/// <summary>
/// 按「实际水平移速 / 当前动作设计移速」缩放 Animator 播放速率，
/// 让支撑脚后移速度跟上角色平移，消除打滑/溜冰（Footskate）。
/// 行走与奔跑用各自的设计移速；待机时恢复 1×。
/// </summary>
[RequireComponent(typeof(Animator))]
public class CharacterFootskateFix : MonoBehaviour
{
    const float WalkThreshold = 0.1f;
    const float MoveEpsilon = 0.01f;

    [Header("设计基准参数")]
    [SerializeField] float walkMoveSpeed = QingfengWalkStride.DesignMoveSpeed;
    [SerializeField] float runMoveSpeed = QingfengRunStride.DesignMoveSpeed;
    [SerializeField] float baseAnimSpeed = 1f;

    Animator animator;
    CombatActor combat;
    Vector3 lastPos;

    void Awake()
    {
        animator = GetComponent<Animator>();
        combat = GetComponent<CombatActor>();
        lastPos = transform.position;
        walkMoveSpeed = QingfengWalkStride.DesignMoveSpeed;
        runMoveSpeed = QingfengRunStride.DesignMoveSpeed;
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

        float speedParam = 0f;
        if (animator.runtimeAnimatorController != null)
            speedParam = animator.GetFloat("Speed");

        bool locomoting = speedParam > WalkThreshold;
        float baseMove = speedParam >= QingfengRunStride.RunAnimThreshold
            ? runMoveSpeed
            : walkMoveSpeed;

        if (locomoting && currentSpeed > MoveEpsilon && baseMove > 0.01f)
            animator.speed = (currentSpeed / baseMove) * baseAnimSpeed;
        else
            animator.speed = baseAnimSpeed;
    }
}
