namespace MLDeploy.API.Models;

public class MLModel
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string Framework { get; set; } = "sklearn";
    public string Status { get; set; } = "Draft";
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public List<ModelVersion> Versions { get; set; } = new();
    public List<Deployment> Deployments { get; set; } = new();
}

public class ModelVersion
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid ModelId { get; set; }
    public string Version { get; set; } = "1.0.0";
    public string? ExperimentId { get; set; }
    public string? MetricsJson { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

public class Deployment
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid ModelId { get; set; }
    public string Version { get; set; } = "1.0.0";
    public string Status { get; set; } = "Pending";
    public string Environment { get; set; } = "Staging";
    public string? EndpointUrl { get; set; }
    public DateTime DeployedAt { get; set; } = DateTime.UtcNow;
}

public class InferenceLog
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid ModelId { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public double LatencyMs { get; set; }
    public bool IsError { get; set; }
}