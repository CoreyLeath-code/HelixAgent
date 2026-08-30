output "event_bucket_name" {
  description = "S3 bucket receiving compressed HelixAgent lifecycle events."
  value       = aws_s3_bucket.agent_events.bucket
}

output "event_bucket_arn" {
  description = "ARN of the HelixAgent event-lake S3 bucket."
  value       = aws_s3_bucket.agent_events.arn
}

output "firehose_stream_name" {
  description = "Amazon Data Firehose stream name used by HelixAgent producers."
  value       = aws_kinesis_firehose_delivery_stream.agent_events.name
}

output "firehose_stream_arn" {
  description = "ARN of the Amazon Data Firehose stream."
  value       = aws_kinesis_firehose_delivery_stream.agent_events.arn
}

output "agent_event_writer_policy_arn" {
  description = "Least-privilege policy to attach to the HelixAgent workload identity."
  value       = aws_iam_policy.agent_event_writer.arn
}
