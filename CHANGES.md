# Changes

## 2026-06-08

1. Stabilized the legacy Android build by pinning Fabric Gradle tooling and
   moving the project to Android build-tools 24.0.3, which provides a 64-bit
   `aapt` binary on the current Linux build host.
2. Kept Fabric build behavior opt-in through a local `fabricApiKey` property so
   public builds do not require a checked-in private Fabric API key.
3. Added a local JVM unit test around air-quality request URL construction so
   request composition can be verified without an emulator, device, network, or
   Android runtime.
4. Cleaned lint findings by removing a duplicate permission, moving status
   bitmaps to `drawable-nodpi`, extracting UI text into string resources, adding
   an image content description, and explicitly disabling RTL support for this
   legacy layout.
5. Added module-level lint configuration for obsolete SDK-tooling checks that
   Android Gradle Plugin 1.2.3 cannot satisfy with current command-line SDK
   installs, while leaving project lint checks active.
6. Added setup documentation, a modernization plan, and CircleCI that runs lint,
   JVM tests, and a debug APK build.
