import { ReactElement, ReactNode, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import useStore from "@/src/store";
import { usePathname, useRouter } from "next/navigation";
import { initials } from "@dicebear/collection";
import { createAvatar } from "@dicebear/core";
import { axiosInstance } from '@/src/services/axiosInstance';
import { NextPage } from 'next';
import { Avatar, AvatarImage } from '../../ui/avatar';
import { cn } from '@/lib/utils';
import { Button, buttonVariants } from '../../ui/button';
import { DropdownMenu, DropdownMenuShortcut, DropdownMenuTrigger, DropdownMenuGroup, DropdownMenuItem, DropdownMenuContent, DropdownMenuSeparator, DropdownMenuLabel } from '../../ui/dropdown-menu';
import { } from '@radix-ui/react-dropdown-menu';

export type NextPageWithLayout<P = object, IP = P> = NextPage<P, IP> & {
    getLayout?: (page: ReactElement) => ReactNode;
};

export default function Header() {
    const initializeAuth = useStore((state) => state.initializeAuth);
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        initializeAuth();
    }, [initializeAuth]);

    const email = useStore((state) => state.email);
    const role = useStore((state) => state.role);
    const setAccessToken = useStore((state) => state.setAccessToken);

    const svg = createAvatar(initials, {
        seed: email ?? "default-user",
        radius: 50,
        backgroundColor: ["d1d4f9", "ffd5dc", "c0aede"],
    }).toString();

    const handleLogout = async () => {
        await axiosInstance.post('/v1/logout');

        setAccessToken(null);
        router.push("/login");
    };

    return (
        <div className="bg-white border-b border-gray-200">
            <nav className="container mx-auto flex justify-between items-center px-4 py-3">
                {/* Left: Logo and Brand */}
                <Link href="/" className="text-xl font-semibold flex items-center gap-4">
                    <Image
                        src="/yivi-logo.svg"
                        alt="Yivi Logo"
                        height={32}
                        width={54}
                    />
                    Portal
                </Link>

                <div className="md:flex items-center gap-6">
                    <Link href="/organizations" className={cn(buttonVariants({
                        variant: 'ghost',
                        className: pathname === '/organizations' ? 'bg-muted hover:bg-muted' : ''
                    }))}>
                        Organizations
                    </Link>

                    {email ? (
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="ghost" className="relative h-8 w-8 rounded">
                                    <Avatar className="h-9 w-9">
                                        <AvatarImage src={`data:image/svg+xml;utf8,${encodeURIComponent(svg)}`} alt="User Avatar" />
                                    </Avatar>
                                </Button>
                            </DropdownMenuTrigger>

                            <DropdownMenuContent className="w-56" align="end" forceMount>
                                <DropdownMenuLabel className="font-normal">
                                    <div className="flex flex-col space-y-1">
                                        <p className="text-sm font-medium leading-none">{email}</p>
                                        <p className="text-xs leading-none text-muted-foreground">
                                            {role}
                                        </p>
                                    </div>
                                </DropdownMenuLabel>

                                <DropdownMenuSeparator />

                                <DropdownMenuGroup>
                                    <DropdownMenuItem className="!cursor-pointer">
                                        Your organization
                                    </DropdownMenuItem>
                                </DropdownMenuGroup>

                                <DropdownMenuSeparator />

                                <DropdownMenuItem onClick={handleLogout} className="!cursor-pointer">
                                    Log out
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    ) : (
                        <Link href="/login" className={cn(buttonVariants())}>
                            Login
                        </Link>
                    )}
                </div>
            </nav >
        </div >
    );
}
