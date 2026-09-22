/// <summary>
/// 青锋奔跑 9 帧步幅（PPU=214，每帧 45ms，周期 0.405s）。
/// 一个循环两步。拉开时前后靴心距约 140px，世界步幅与行走身高对齐。
/// </summary>
public static class QingfengRunStride
{
    public const float PixelsPerUnit = 214f;
    public const int FrameCount = 9;
    public const int StepsPerCycle = 2;
    public const float FrameSeconds = 0.045f;
    public const float CycleSeconds = FrameCount * FrameSeconds;
    public const float StepDistancePixels = 140f;
    public const float RunAnimThreshold = 0.55f;

    /// <summary>零打滑设计移速（世界单位/秒）。约 3.23。</summary>
    public const float DesignMoveSpeed =
        StepsPerCycle * StepDistancePixels / CycleSeconds / PixelsPerUnit;
}
