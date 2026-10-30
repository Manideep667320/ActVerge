import { Suspense } from "react";
import TaskDetailClient from "./TaskDetailClient";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function TaskDetailPage({ params }: PageProps) {
  const { id } = await params;
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center h-screen">
          <div className="text-muted-foreground animate-pulse">
            Loading task…
          </div>
        </div>
      }
    >
      <TaskDetailClient taskId={id} />
    </Suspense>
  );
}
