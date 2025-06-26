import AppRoutes from "./routes";
import { Toaster } from "sonner";
import { useIdleRefresh, useAuthInit } from "@/store";

function App() {
  useIdleRefresh();
  useAuthInit();
  return (
    <div>
      <AppRoutes />
      <Toaster richColors />
    </div>
  );
}

export default App;
