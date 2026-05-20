using Microsoft.AspNetCore.Mvc;
using MLDeploy.API.Data;
using MLDeploy.API.Models;
using Microsoft.EntityFrameworkCore;

namespace MLDeploy.API.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ModelsController : ControllerBase
{
    private readonly AppDbContext _db;

    public ModelsController(AppDbContext db)
    {
        _db = db;
    }

    // GET: api/models
    [HttpGet]
    public async Task<ActionResult<List<MLModel>>> GetAll() =>
        await _db.Models.Include(m => m.Versions).ToListAsync();

    // GET: api/models/{id}
    [HttpGet("{id:guid}")]
    public async Task<ActionResult<MLModel>> GetById(Guid id)
    {
        var model = await _db.Models
            .Include(m => m.Versions)
            .Include(m => m.Deployments)
            .FirstOrDefaultAsync(m => m.Id == id);

        return model == null ? NotFound() : Ok(model);
    }

    // POST: api/models
    [HttpPost]
    public async Task<ActionResult<MLModel>> Create([FromBody] CreateModelRequest request)
    {
        var model = new MLModel
        {
            Name = request.Name,
            Description = request.Description,
            Framework = request.Framework
        };

        _db.Models.Add(model);
        await _db.SaveChangesAsync();

        return CreatedAtAction(nameof(GetById), new { id = model.Id }, model);
    }

    // DELETE: api/models/{id}
    [HttpDelete("{id:guid}")]
    public async Task<IActionResult> Delete(Guid id)
    {
        var model = await _db.Models.FindAsync(id);
        if (model == null) return NotFound();

        _db.Models.Remove(model);
        await _db.SaveChangesAsync();
        return NoContent();
    }
}

// Request DTO (Data Transfer Object)
public record CreateModelRequest(string Name, string? Description, string Framework);