'use client';

import Link from 'next/link';
import { useParams, usePathname } from 'next/navigation';

import { cn } from '@/lib/utils';
import { buttonVariants } from '@/src/components/ui/button';

interface SidebarNavigationProps extends React.HTMLAttributes<HTMLElement> {
    items: {
        href: string;
        title: string;
    }[];
}

export function SidebarNavigation({ className, items, ...props }: SidebarNavigationProps) {
    const pathname = usePathname();
    const params = useParams();

    return (
        <nav
            className={cn(
                "flex space-x-2 lg:flex-col lg:space-x-0 lg:space-y-1",
                className
            )}
            {...props}
        >
            {items.map((item) => (
                <Link
                    key={item.href}
                    href={{
                        pathname: item.href,
                        query: { organization: params?.organization },
                    }}
                    className={cn(
                        buttonVariants({ variant: "ghost" }),
                        pathname === item.href
                            ? "bg-muted hover:bg-muted"
                            : "hover:bg-transparent hover:underline",
                        "!justify-start"
                    )}
                >
                    {item.title}
                </Link>
            ))}
        </nav>
    );
}