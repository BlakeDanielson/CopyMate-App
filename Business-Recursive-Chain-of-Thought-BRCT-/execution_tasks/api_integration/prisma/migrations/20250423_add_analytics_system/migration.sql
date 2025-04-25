-- CreateTable
CREATE TABLE "ApiPerformanceLog" (
    "id" TEXT NOT NULL,
    "endpoint" TEXT NOT NULL,
    "method" TEXT NOT NULL,
    "statusCode" INTEGER NOT NULL,
    "responseTime" INTEGER NOT NULL,
    "userId" TEXT,
    "timestamp" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "metadata" JSONB,

    CONSTRAINT "ApiPerformanceLog_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "LlmPerformanceLog" (
    "id" TEXT NOT NULL,
    "provider" TEXT NOT NULL,
    "model" TEXT NOT NULL,
    "operation" TEXT NOT NULL,
    "timeToFirstToken" INTEGER,
    "totalDuration" INTEGER NOT NULL,
    "tokenCount" INTEGER,
    "success" BOOLEAN NOT NULL,
    "errorCode" TEXT,
    "errorMessage" TEXT,
    "userId" TEXT,
    "timestamp" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "metadata" JSONB,

    CONSTRAINT "LlmPerformanceLog_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "PerformanceAggregate" (
    "id" TEXT NOT NULL,
    "metricType" TEXT NOT NULL,
    "metricTarget" TEXT NOT NULL,
    "timeWindow" TEXT NOT NULL,
    "timestamp" TIMESTAMP(3) NOT NULL,
    "value" DOUBLE PRECISION NOT NULL,
    "sampleCount" INTEGER NOT NULL,
    "p50" DOUBLE PRECISION,
    "p95" DOUBLE PRECISION,
    "p99" DOUBLE PRECISION,
    "metadata" JSONB,

    CONSTRAINT "PerformanceAggregate_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "ApiPerformanceLog_endpoint_idx" ON "ApiPerformanceLog"("endpoint");
CREATE INDEX "ApiPerformanceLog_timestamp_idx" ON "ApiPerformanceLog"("timestamp");
CREATE INDEX "ApiPerformanceLog_userId_idx" ON "ApiPerformanceLog"("userId");

-- CreateIndex
CREATE INDEX "LlmPerformanceLog_provider_model_idx" ON "LlmPerformanceLog"("provider", "model");
CREATE INDEX "LlmPerformanceLog_timestamp_idx" ON "LlmPerformanceLog"("timestamp");
CREATE INDEX "LlmPerformanceLog_userId_idx" ON "LlmPerformanceLog"("userId");
CREATE INDEX "LlmPerformanceLog_success_idx" ON "LlmPerformanceLog"("success");

-- CreateIndex
CREATE INDEX "PerformanceAggregate_metricType_metricTarget_idx" ON "PerformanceAggregate"("metricType", "metricTarget");
CREATE INDEX "PerformanceAggregate_timeWindow_timestamp_idx" ON "PerformanceAggregate"("timeWindow", "timestamp");
