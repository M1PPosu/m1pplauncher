using System.Linq;
using System.Net.Http;
using System.Text.Json.Nodes;
using System.Threading.Tasks;

namespace m1pplauncher.Services;

internal static class UpdateCheckerService
{
  public const string REPO = "m1pposu/m1pplauncher";
  public const string TAG_NAME = $"v{App.VERSION_BASE}";
  private const string RELEASES_API_URL = $"https://api.github.com/repos/{REPO}/releases";

  public static async Task<string?> IsLatestVersionAsync()
  {
    using HttpClient http = new();
    http.DefaultRequestHeaders.UserAgent.ParseAdd("m1pplauncher/" + App.VERSION_BASE);
    string json = await http.GetStringAsync(RELEASES_API_URL);

    string? newestTagName = JsonNode.Parse(json)?.AsArray().FirstOrDefault()?["tag_name"]?.GetValue<string>();
    if(newestTagName == TAG_NAME)
      return null;

    return newestTagName;
  }
}
