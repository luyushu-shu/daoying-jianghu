/// <summary>
/// 一帧内的操作意图。玩家由输入缓冲填入，敌人由 AI 填入。
/// 一次性意图被状态消费后要清零；持续意图（blockHeld / skill2Held / moveX）每帧重写。
/// </summary>
public struct Intents
{
    public float moveX;      // -1..1
    public bool light;       // 轻击
    public bool heavy;       // 重击（空中=下重砸）
    public bool skill1;      // 破空刺
    public bool skill2;      // 一剑霜寒
    public bool dodge;       // 闪避
    public bool jump;        // 轻功（W+闪避）
    public bool dash;        // 冲刺
    public bool blockHeld;   // 格挡按住
    public bool skill2Held;  // 蓄力按住

    public void ClearOneShots()
    {
        light = heavy = skill1 = skill2 = dodge = jump = dash = false;
    }
}
