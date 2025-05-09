import { Link, useLocation, useParams } from "react-router-dom";
import { cn } from "@/lib/utils";
import { buttonVariants } from "@/components/ui/button";

interface SidebarNavigationProps extends React.HTMLAttributes<HTMLElement> {
  items: {
    href: string;
    title: string;
  }[];
}

export function SidebarNavigation({
  className,
  items,
  ...props
}: SidebarNavigationProps) {
  const location = useLocation();
  const params = useParams();
  const currentPath = location.pathname;

  return (
    <nav
      className={cn(
        "flex space-x-2 lg:flex-col lg:space-x-0 lg:space-y-1",
        className
      )}
      {...props}
    >
      {items.map((item) => {
        const itemHref = item.href.replace(
          ":organization",
          params?.organization || ""
        );

        return (
          <Link
            key={item.href}
            to={itemHref}
            className={cn(
              buttonVariants({ variant: "ghost" }),
              currentPath === itemHref
                ? "bg-muted hover:bg-muted"
                : "hover:bg-transparent hover:underline",
              "!justify-start"
            )}
          >
            {item.title}
          </Link>
        );
      })}
    </nav>
  );
}
