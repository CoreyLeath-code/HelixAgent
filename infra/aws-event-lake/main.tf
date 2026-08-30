locals {
  common_tags = merge(
    {
      Project   = "HelixAgent"
      ManagedBy = "Terraform"
      Component = "agent-event-lake"
    },
    var.tags,
  )
}

resource "aws_s3_bucket" "agent_events" {
  bucket_prefix = "${var.project_name}-agent-events-"
  tags          = local.common_tags
}

resource "aws_s3_bucket_public_access_block" "agent_events" {
  bucket = aws_s3_bucket.agent_events.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "agent_events" {
  bucket = aws_s3_bucket.agent_events.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "agent_events" {
  bucket = aws_s3_bucket.agent_events.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "agent_events" {
  bucket = aws_s3_bucket.agent_events.id

  rule {
    id     = "agent-event-retention"
    status = "Enabled"

    filter {}

    expiration {
      days = var.retention_days
    }

    noncurrent_version_expiration {
      noncurrent_days = var.retention_days
    }
  }

  depends_on = [aws_s3_bucket_versioning.agent_events]
}

resource "aws_cloudwatch_log_group" "firehose" {
  name              = "/aws/firehose/${var.firehose_stream_name}"
  retention_in_days = var.cloudwatch_log_retention_days
  tags              = local.common_tags
}

resource "aws_cloudwatch_log_stream" "firehose" {
  name           = "S3Delivery"
  log_group_name = aws_cloudwatch_log_group.firehose.name
}

data "aws_iam_policy_document" "firehose_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["firehose.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "firehose_delivery" {
  name_prefix        = "${var.project_name}-firehose-delivery-"
  assume_role_policy = data.aws_iam_policy_document.firehose_assume_role.json
  tags               = local.common_tags
}

data "aws_iam_policy_document" "firehose_delivery" {
  statement {
    sid = "ReadBucketMetadata"
    actions = [
      "s3:GetBucketLocation",
      "s3:ListBucket",
      "s3:ListBucketMultipartUploads",
    ]
    resources = [aws_s3_bucket.agent_events.arn]
  }

  statement {
    sid = "WriteEventObjects"
    actions = [
      "s3:AbortMultipartUpload",
      "s3:GetObject",
      "s3:PutObject",
    ]
    resources = ["${aws_s3_bucket.agent_events.arn}/*"]
  }

  statement {
    sid       = "WriteDeliveryLogs"
    actions   = ["logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.firehose.arn}:*"]
  }
}

resource "aws_iam_role_policy" "firehose_delivery" {
  name   = "${var.project_name}-firehose-s3-delivery"
  role   = aws_iam_role.firehose_delivery.id
  policy = data.aws_iam_policy_document.firehose_delivery.json
}

resource "aws_kinesis_firehose_delivery_stream" "agent_events" {
  name        = var.firehose_stream_name
  destination = "extended_s3"
  tags        = local.common_tags

  extended_s3_configuration {
    role_arn           = aws_iam_role.firehose_delivery.arn
    bucket_arn         = aws_s3_bucket.agent_events.arn
    buffering_size     = var.buffer_size_mib
    buffering_interval = var.buffer_interval_seconds
    compression_format = "GZIP"

    prefix              = "events/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/hour=!{timestamp:HH}/"
    error_output_prefix = "errors/!{firehose:error-output-type}/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/hour=!{timestamp:HH}/"

    cloudwatch_logging_options {
      enabled         = true
      log_group_name  = aws_cloudwatch_log_group.firehose.name
      log_stream_name = aws_cloudwatch_log_stream.firehose.name
    }
  }

  depends_on = [
    aws_iam_role_policy.firehose_delivery,
    aws_s3_bucket_public_access_block.agent_events,
    aws_s3_bucket_server_side_encryption_configuration.agent_events,
  ]
}

data "aws_iam_policy_document" "agent_event_writer" {
  statement {
    sid = "WriteAgentEvents"
    actions = [
      "firehose:PutRecord",
      "firehose:PutRecordBatch",
    ]
    resources = [aws_kinesis_firehose_delivery_stream.agent_events.arn]
  }
}

resource "aws_iam_policy" "agent_event_writer" {
  name_prefix = "${var.project_name}-agent-event-writer-"
  description = "Allows HelixAgent workloads to publish redacted lifecycle events to Data Firehose."
  policy      = data.aws_iam_policy_document.agent_event_writer.json
  tags        = local.common_tags
}
