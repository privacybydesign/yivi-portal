import AppRoutes from "./routes";
import { Toaster } from "sonner";

function App() {
  return (
    <div>
      <AppRoutes />
      <Toaster richColors />
    </div>
  );
}

export default App;
