import { Component, type ErrorInfo, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { Button, buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type Props = {
  children: ReactNode;
  // Changing this clears the fallback, so navigating away from a broken page
  // brings the app back without a full reload.
  resetKey?: string;
};

type State = {
  hasError: boolean;
};

// Without a boundary any error thrown while rendering or committing unmounts
// the entire React root, which leaves the user staring at a blank page.
export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Unhandled error while rendering:", error, info.componentStack);
  }

  componentDidUpdate(prevProps: Props) {
    if (this.state.hasError && prevProps.resetKey !== this.props.resetKey) {
      this.setState({ hasError: false });
    }
  }

  render() {
    if (!this.state.hasError) {
      return this.props.children;
    }

    return (
      <div
        className="mx-auto max-w-lg rounded-lg border bg-white p-6 text-center shadow"
        data-testid="error-boundary-fallback"
      >
        <h1 className="text-xl font-semibold">Something went wrong</h1>
        <p className="mt-2 text-sm text-gray-500">
          This page could not be displayed. Try again, or go back to the
          homepage.
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <Button onClick={() => window.location.reload()}>Try again</Button>
          <Link to="/" className={cn(buttonVariants({ variant: "outline" }))}>
            Back to home
          </Link>
        </div>
      </div>
    );
  }
}
