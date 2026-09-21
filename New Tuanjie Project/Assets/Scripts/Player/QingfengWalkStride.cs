/// <summary>
/// 青锋行走 8 帧的步幅元数据（PPU=100，12 FPS）。
/// 支撑脚相对轴心后移：F1–F4 约 74.4px，F5–F8 约 72.9px。
/// 设计移速 = 步幅像素 × (FPS / 每步帧数) / PPU。
/// </summary>
public static class QingfengWalkStride
{
    public const float Fps = 12f;
    public const float PixelsPerUnit = 100f;
    public const int FramesPerStep = 4;
    public const float StepDistancePixels = 73.65f;

    /// <summary>零打滑设计移速（世界单位/秒）。约 2.21。</summary>
    public const float DesignMoveSpeed =
        StepDistancePixels * (Fps / FramesPerStep) / PixelsPerUnit;
}
