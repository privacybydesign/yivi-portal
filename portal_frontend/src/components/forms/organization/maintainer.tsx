"use client";

import { useActionState, useEffect, useState } from "react";
import { useForm } from 'react-hook-form';
import { Button, buttonVariants } from "@/src/components/ui/button";
import { Input } from "@/src/components/ui/input";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/src/components/ui/dialog';
import { Form, FormControl, FormDescription, FormField, FormItem, FormMessage } from "@/src/components/ui/form";
import { Label } from "@/src/components/ui/label";
import { addMaintainerForOrganization, RegistrationFormState, MaintainerRegistrationInputs } from "@/src/actions/manage-maintainer";
import { Organization } from '@/src/models/organization';
import { cn } from '@/lib/utils';
import { toast } from '@/hooks/use-toast';

export default function AddOrganizationMaintainerInformationForm(
    { organization, onCreate }: { organization: Organization; onCreate: (organisationSlug: string) => unknown; }
) {
    const [defaultFormInput] = useState({
        email: '',
        organizationSlug: organization.slug,
    } as MaintainerRegistrationInputs);
    const [modalIsOpen, setModalIsOpen] = useState(false);

    const [formState, formSubmit, pending] = useActionState<
        RegistrationFormState,
        FormData
    >(addMaintainerForOrganization, {
        values: defaultFormInput,
        errors: {},
    });

    const form = useForm<MaintainerRegistrationInputs>({
        defaultValues: defaultFormInput,
    });

    useEffect(() => {
        form.clearErrors();

        if (formState?.errors) {
            Object.entries(formState.errors).forEach(([field, error]) => {
                if (error?.message) {
                    form.setError((field as keyof MaintainerRegistrationInputs), {
                        type: "server",
                        message: error.message,
                    });
                }
            });
        }
    }, [formState?.errors, form]);

    useEffect(() => {
        if (formState.success) {
            setModalIsOpen(false);
            onCreate(organization.slug);

            toast({
                title: 'Success',
                description: 'The user was created and added to this organization.'
            });

            // Will prevent the dialog from closing directly when opened again.
            formState.success = false;
            form.reset();
        }

    }, [form, formState, organization, onCreate]);

    return (
        <Dialog open={modalIsOpen} onOpenChange={setModalIsOpen}>
            <DialogTrigger className={cn(buttonVariants())}>
                Add maintainer
            </DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Add maintainer</DialogTitle>
                    <DialogDescription>
                        This person will get the rights to update this organization&apos;s information.
                    </DialogDescription>
                </DialogHeader>

                <Form {...form}>
                    <form action={formSubmit} className="space-y-4">
                        <FormField
                            control={form.control}
                            name="email"
                            render={({ field }) => (
                                <FormItem className="grid md:grid-cols-2 items-start md:gap-x-4">
                                    <div className="py-1">
                                        <Label>Email address</Label>
                                        <FormDescription>
                                            Email address of the maintainer
                                        </FormDescription>
                                    </div>
                                    <FormControl>
                                        <Input type="email" {...field} />
                                    </FormControl>
                                    {formState.errors.email && (
                                        <FormMessage className="col-span-2 text-sm text-red-600 mt-1">
                                            {!formState.errors.email.message}
                                        </FormMessage>
                                    )}
                                </FormItem>
                            )}
                        />

                        {formState?.globalError && (
                            <div className="col-span-2 text-sm text-red-600 font-medium">
                                {formState.globalError}
                            </div>
                        )}

                        <div className="flex sm:justify-end">
                            <Button type="submit" disabled={pending} className="col-span-2">
                                {pending ? "Submitting..." : "Submit"}
                            </Button>
                        </div>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    );
}
