Import("env")


def print_memory_report(source, target, build_env):
    elf = str(source[0])
    print("\nPacket Loss ESP32-S3 memory report")
    print("Firmware flash budget: 2,621,440 bytes; PSRAM runtime budget: 4,194,304 bytes")
    build_env.Execute('%s -A "%s"' % (build_env.subst("$SIZE"), elf))


env.AddPostAction("$BUILD_DIR/${PROGNAME}.elf", print_memory_report)
