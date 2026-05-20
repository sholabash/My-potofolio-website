using Microsoft.AspNetCore.Mvc;
using MLDeploy.API.Data;
using Microsoft.EntityFrameworkCore;

namespace MLDeploy.API.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DashboardController : ControllerBase
{
    private readonly AppDbContext _db;

    public DashboardController(AppDbContext db)
    {
        _db = db;
    }

    // GET: api/dashboard/stats
    [HttpGet("stats")]
    public async Task<ActionResult<object>> GetStats()
    {
        var totalModels = await _db.Models.CountAsync();
        var activeDeployments = await _db.Deployments.CountAsync(d => d.Status == "Running");
        var totalPredictions = await _db.InferenceLogs.CountAsync();

        return Ok(new
        {
            TotalModels = totalModels,
            ActiveDeployments = activeDeployments,
            TotalPredictions = totalPredictions,
            LastUpdated = DateTime.UtcNow
        });
    }
}