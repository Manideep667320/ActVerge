import ResultsTable from "@/components/ResultsTable";
import BenchmarkMetrics from "@/components/BenchmarkMetrics";

export const dynamic = "force-dynamic";

export default function ResultsPage() {
  return (
    <div className="px-6 py-8 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">Evaluation & Verification Benchmark</h1>
        <p className="text-muted-foreground mt-1 text-sm">
          Autonomous outcome verification metrics, agent failure interception, and task audit ledger.
        </p>
      </div>
      <BenchmarkMetrics />
      <ResultsTable />
    </div>
  );
}
