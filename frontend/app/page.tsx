import TaskForm from "@/components/TaskForm";
import RecentTasks from "@/components/RecentTasks";

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero section */}
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-16 gap-10">
        {/* Branding */}
        <div className="flex flex-col items-center gap-3 text-center">
          <div className="flex items-center gap-3">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/actverge-logo.svg"
              alt="ActVerge Logo"
              className="h-10 w-10"
            />
            <h1 className="text-4xl font-bold tracking-tight">
              Act<span className="text-primary">Verge</span>
            </h1>
          </div>
          <p className="text-muted-foreground text-lg max-w-md">
            Submit a task and watch AI agents execute, verify, and recover in
            real time.
          </p>
        </div>

        {/* Task submission form */}
        <div className="w-full max-w-2xl">
          <TaskForm />
        </div>

        {/* Recent tasks */}
        <div className="w-full max-w-2xl">
          <RecentTasks />
        </div>
      </div>
    </div>
  );
}
