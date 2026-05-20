using Microsoft.EntityFrameworkCore;
using MLDeploy.API.Models;

namespace MLDeploy.API.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<MLModel> Models => Set<MLModel>();
    public DbSet<ModelVersion> ModelVersions => Set<ModelVersion>();
    public DbSet<Deployment> Deployments => Set<Deployment>();
    public DbSet<InferenceLog> InferenceLogs => Set<InferenceLog>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<MLModel>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.Name);
        });

        modelBuilder.Entity<Deployment>(entity =>
        {
            entity.HasOne<MLModel>()
                .WithMany(m => m.Deployments)
                .HasForeignKey(d => d.ModelId);
        });
    }
}