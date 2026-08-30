variable "aws_region" {
  description = "AWS Region for the Firehose stream and S3 bucket."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Prefix used for AWS resource names and tags."
  type        = string
  default     = "helixagent"
}

variable "firehose_stream_name" {
  description = "Amazon Data Firehose delivery stream name."
  type        = string
  default     = "helixagent-agent-events"
}

variable "retention_days" {
  description = "Days to retain current and noncurrent S3 event objects."
  type        = number
  default     = 30

  validation {
    condition     = var.retention_days >= 1
    error_message = "retention_days must be at least 1."
  }
}

variable "buffer_size_mib" {
  description = "Approximate Firehose S3 delivery buffer size in MiB."
  type        = number
  default     = 5

  validation {
    condition     = var.buffer_size_mib >= 1 && var.buffer_size_mib <= 128
    error_message = "buffer_size_mib must be between 1 and 128."
  }
}

variable "buffer_interval_seconds" {
  description = "Approximate Firehose S3 delivery buffer interval in seconds."
  type        = number
  default     = 60

  validation {
    condition     = var.buffer_interval_seconds >= 60 && var.buffer_interval_seconds <= 900
    error_message = "buffer_interval_seconds must be between 60 and 900."
  }
}

variable "cloudwatch_log_retention_days" {
  description = "CloudWatch retention for Firehose delivery logs."
  type        = number
  default     = 14
}

variable "tags" {
  description = "Additional tags applied to supported AWS resources."
  type        = map(string)
  default     = {}
}
