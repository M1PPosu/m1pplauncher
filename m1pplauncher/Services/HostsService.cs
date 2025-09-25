using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

namespace m1pplauncher.Services;

internal static class HostsService
{
  private static readonly string HOSTS_FILE = Path.Combine(Environment.GetEnvironmentVariable("windir")!, "system32", "drivers", "etc", "hosts");
  private const string IS_BLOCKED_IDENTIFIER = "m1pplauncher";
  private static readonly string[] PPY_DOMAINS = [
    "ppy.sh",
    "osu.ppy.sh",
    "c.ppy.sh",
    "c1.ppy.sh",
    "c2.ppy.sh",
    "c3.ppy.sh",
    "c4.ppy.sh",
    "c5.ppy.sh",
    "c6.ppy.sh",
    "ce.ppy.sh",
    "a.ppy.sh",
    "i.ppy.sh"
  ];

  public static async Task<bool> IsPpyBlockedAsync() => (await File.ReadAllTextAsync(HOSTS_FILE)).Contains(IS_BLOCKED_IDENTIFIER);

  public static async Task BlockPpyAsync()
  {
    await File.AppendAllLinesAsync(HOSTS_FILE, PPY_DOMAINS.Select(x => $"127.0.0.1 {x} # {IS_BLOCKED_IDENTIFIER}"));
  }

  public static async Task UnblockPpyAsync()
  {
    string[] lines = await File.ReadAllLinesAsync(HOSTS_FILE);
    await File.WriteAllLinesAsync(HOSTS_FILE, lines.Where(line => !line.Contains(IS_BLOCKED_IDENTIFIER)));
  }
}
