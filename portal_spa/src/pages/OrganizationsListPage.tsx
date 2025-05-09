import { useState, useEffect } from "react";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { axiosInstance } from "@/services/axiosInstance";
import { useSearchParams, Link } from "react-router-dom";
import type { PaginationResponse } from "@/models/paginated-response";
import type { Organization } from "@/models/organization";

export default function OrganizationsListPage() {
  const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;
  const [searchParams, setSearchParams] = useSearchParams();

  const [searchQuery, setSearchQuery] = useState(
    searchParams.get("search") || ""
  );
  const [selectedTrustModel, setSelectedTrustModel] = useState(
    searchParams.get("trust_model") || "all"
  );
  const [APSelected, setAPSelected] = useState(
    !searchParams.has("ap") || searchParams.get("ap") === "true"
  );
  const [RPSelected, setRPSelected] = useState(
    !searchParams.has("rp") || searchParams.get("rp") === "true"
  );
  const [currentPage, setCurrentPage] = useState(() => {
    const page = searchParams.get("page");
    return page ? parseInt(page) : 1;
  });

  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [trustModels, setTrustModels] = useState<string[]>([]);
  const [applyingFilters, setApplyingFilters] = useState(false);

  // Pagination state
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const pageSize = 20; // Fixed page size

  // Function to fetch organizations with pagination
  const fetchOrganizations = (
    page = 1,
    selectAPs: boolean,
    selectRPs: boolean
  ) => {
    setLoading(true);
    const offset = (page - 1) * pageSize;

    // Base URL with pagination
    let url = `${apiEndpoint}/v1/organizations/?limit=${pageSize}&offset=${offset}`;

    // Add search if present
    if (searchQuery && searchQuery.trim() !== "") {
      url += `&search=${encodeURIComponent(searchQuery.trim())}`;
    }

    // Add trust model filter
    if (selectedTrustModel !== "all") {
      url += `&trust_model=${encodeURIComponent(selectedTrustModel)}`;
    }

    url += `&rp=${selectRPs}`;
    url += `&ap=${selectAPs}`;

    axiosInstance
      .get<PaginationResponse<Organization>>(url)
      .then((response) => {
        const data = response.data;

        setTotalCount(data.count);
        setTotalPages(Math.ceil(data.count / pageSize));
        setOrganizations(data.results);

        // Extract trust models if not already done
        if (trustModels.length === 0) {
          const models = [
            ...new Set(data.results.map((org) => org.trust_model)),
          ].filter(Boolean);
          setTrustModels(models);
        }

        setLoading(false);
        setApplyingFilters(false);
      })
      .catch((error) => {
        console.error("Error fetching organizations:", error);
        setLoading(false);
        setApplyingFilters(false);
      });
  };

  const updateQueryParams = (params: Record<string, string | undefined>) => {
    const newParams = new URLSearchParams(searchParams.toString());
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        newParams.set(key, value);
      } else {
        newParams.delete(key);
      }
    });
    setSearchParams(newParams);
  };

  useEffect(() => {
    const page = parseInt(searchParams.get("page") || "1");
    const search = searchParams.get("search") || "";
    const trustModel = searchParams.get("trust_model") || "all";
    const selectAPs =
      !searchParams.has("ap") || searchParams.get("ap") === "true";
    const selectRPs =
      !searchParams.has("rp") || searchParams.get("rp") === "true";
    setSearchQuery(search);
    setSelectedTrustModel(trustModel);
    setAPSelected(selectAPs);
    setRPSelected(selectRPs);
    setCurrentPage(page);

    fetchOrganizations(page, selectAPs, selectRPs);
  }, [searchParams.toString()]);

  // Function to apply filters
  const applyFilters = (
    searchQuery: string,
    selectedTrustModel: string,
    selectAPs: boolean,
    selectRPs: boolean
  ) => {
    setApplyingFilters(true);
    updateQueryParams({
      page: "1",
      search: searchQuery || undefined,
      trust_model:
        selectedTrustModel !== "all" ? selectedTrustModel : undefined,
      ap: selectAPs ? "true" : "false",
      rp: selectRPs ? "true" : "false",
    });
  };

  const handleFilterChange = (ap: boolean, rp: boolean, trustModel: string) => {
    applyFilters(searchQuery, trustModel, ap, rp);
  };

  // Handle search input change with debounce to stop rapid call to API
  const handleSearch = (value: string) => {
    setSearchQuery(value);
    applyFilters(value, selectedTrustModel, APSelected, RPSelected);
  };

  // Handle page change
  const handlePageChange = (newPage: number) => {
    if (newPage > 0 && newPage <= totalPages) {
      setCurrentPage(newPage);
      updateQueryParams({ page: newPage.toString() });
    }
  };

  // Generate page numbers array for pagination
  const getPageNumbers = () => {
    const pageNumbers = [];

    // If few pages, show all
    if (totalPages <= 5) {
      for (let i = 1; i <= totalPages; i++) {
        pageNumbers.push(i);
      }
    } else {
      // Always show first page
      pageNumbers.push(1);

      // Show ellipsis or pages around current
      if (currentPage > 3) {
        pageNumbers.push("...");
      }

      // Pages around current
      const startPage = Math.max(2, currentPage - 1);
      const endPage = Math.min(totalPages - 1, currentPage + 1);

      for (let i = startPage; i <= endPage; i++) {
        pageNumbers.push(i);
      }

      // Show ellipsis if needed
      if (currentPage < totalPages - 2) {
        pageNumbers.push("...");
      }

      // Always show last page
      pageNumbers.push(totalPages);
    }

    return pageNumbers;
  };

  // Calculate visible range for current page
  const getVisibleRange = () => {
    const start = (currentPage - 1) * pageSize + 1;
    const end = Math.min(currentPage * pageSize, totalCount);
    return { start, end };
  };

  return (
    <div className="container mx-auto p-4">
      <div className="flex flex-col gap-6 mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-2xl font-bold">Organizations</h1>
          </div>
        </div>

        <div className="border rounded-md p-4 bg-gray-50">
          <h2 className="text-lg font-medium mb-4">Filters</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label
                htmlFor="search"
                className="block text-sm font-medium mb-1"
              >
                Search
              </label>
              <input
                id="search"
                type="text"
                placeholder="Search organizations..."
                className="w-full px-3 py-2 border rounded-md"
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                onKeyDown={(e) =>
                  e.key === "Enter" &&
                  applyFilters(
                    searchQuery,
                    selectedTrustModel,
                    APSelected,
                    RPSelected
                  )
                }
              />
            </div>

            <div>
              <label
                htmlFor="trustModel"
                className="block text-sm font-medium mb-1"
              >
                Trust Model
              </label>
              <select
                id="trustModel"
                value={selectedTrustModel}
                onChange={(e) => setSelectedTrustModel(e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="all">All Trust Models</option>
                {trustModels.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex flex-wrap gap-6 mb-4">
            <div className="flex items-center space-x-2 p-2 rounded hover:bg-gray-100">
              <Checkbox
                id="isAP"
                checked={APSelected}
                onCheckedChange={() =>
                  handleFilterChange(
                    !APSelected,
                    RPSelected,
                    selectedTrustModel
                  )
                }
              />
              <label
                htmlFor="isAP"
                className="text-sm font-medium leading-none cursor-pointer"
                onClick={() =>
                  handleFilterChange(
                    !APSelected,
                    RPSelected,
                    selectedTrustModel
                  )
                }
              >
                Attestation Provider
              </label>
            </div>

            <div className="flex items-center space-x-2 p-2 rounded hover:bg-gray-100">
              <Checkbox
                id="isRP"
                checked={RPSelected}
                onCheckedChange={() =>
                  handleFilterChange(
                    APSelected,
                    !RPSelected,
                    selectedTrustModel
                  )
                }
              />
              <label
                htmlFor="isRP"
                className="text-sm font-medium leading-none cursor-pointer"
                onClick={() =>
                  handleFilterChange(
                    APSelected,
                    !RPSelected,
                    selectedTrustModel
                  )
                }
              >
                Relying Party
              </label>
            </div>
          </div>

          {(APSelected ||
            RPSelected ||
            selectedTrustModel !== "all" ||
            searchQuery) && (
            <div className="mt-4 text-sm text-blue-600">
              Filtering:
              {searchQuery && ` Search: "${searchQuery}"`}
              {selectedTrustModel !== "all" &&
                ` Trust Model: ${selectedTrustModel}`}
              {APSelected && " | Attestation Providers"}
              {RPSelected && " | Relying Parties"}
            </div>
          )}
        </div>
      </div>

      <Table>
        <TableCaption>
          {!loading && !applyingFilters && (
            <>
              Showing {totalCount > 0 ? getVisibleRange().start : 0} to{" "}
              {getVisibleRange().end} of {totalCount} organizations
              {totalPages > 1 && ` (Page ${currentPage} of ${totalPages})`}
            </>
          )}
        </TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead className="w-16">Logo</TableHead>
            <TableHead>Name</TableHead>
            <TableHead>Trust Model</TableHead>
            <TableHead>AP</TableHead>
            <TableHead>RP</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {loading || applyingFilters ? (
            <TableRow>
              <TableCell colSpan={5} className="text-center py-4 text-gray-500">
                {applyingFilters
                  ? "Applying filters..."
                  : "Loading organizations..."}
              </TableCell>
            </TableRow>
          ) : (
            <>
              {organizations.length > 0 ? (
                organizations.map((org) => (
                  <TableRow key={org.id}>
                    <TableCell>
                      {org.logo ? (
                        <div className="relative h-8 w-8 rounded-full overflow-hidden border border-gray-200">
                          <img
                            src={`${apiEndpoint}${org.logo}`}
                            width={32}
                            height={32}
                            alt={`${org.name_en} logo`}
                            className="object-cover w-full h-full"
                            // onError={(e) => {
                            //   // e.currentTarget.src = "/placeholder-logo.png";
                            // }}
                          />
                        </div>
                      ) : (
                        <div className="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center">
                          <span className="text-gray-500 text-sm font-medium">
                            {org.name_en.charAt(0)}
                          </span>
                        </div>
                      )}
                    </TableCell>
                    <TableCell className="font-medium">
                      <Link
                        to={`/organizations/${org.slug}`}
                        className="hover:text-blue-600"
                      >
                        {org.name_en}
                      </Link>
                    </TableCell>
                    <TableCell>{org.trust_model}</TableCell>
                    <TableCell>
                      {org.is_AP === true ? (
                        <Badge className="bg-green-100 text-green-800">
                          Yes
                        </Badge>
                      ) : (
                        <Badge variant="outline">No</Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      {org.is_RP === true ? (
                        <Badge className="bg-green-100 text-green-800">
                          Yes
                        </Badge>
                      ) : (
                        <Badge variant="outline">No</Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell
                    colSpan={5}
                    className="text-center py-4 text-gray-500"
                  >
                    No organizations found matching your criteria
                  </TableCell>
                </TableRow>
              )}
            </>
          )}
        </TableBody>
      </Table>

      {/* Pagination controls */}
      {totalPages > 1 && (
        <div className="flex justify-between items-center mt-6">
          <div className="text-sm text-gray-500">
            Showing {totalCount > 0 ? getVisibleRange().start : 0} to{" "}
            {getVisibleRange().end} of {totalCount} organizations
          </div>

          <div className="flex-1 flex justify-center">
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1 || loading}
              >
                Previous
              </Button>

              {getPageNumbers().map((page, index) => (
                <Button
                  key={index}
                  variant={page === currentPage ? "default" : "outline"}
                  size="sm"
                  onClick={() =>
                    typeof page === "number" && handlePageChange(page)
                  }
                  disabled={typeof page !== "number" || loading}
                >
                  {page}
                </Button>
              ))}

              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages || loading}
              >
                Next
              </Button>
            </div>
          </div>

          <div className="invisible text-sm text-gray-500">
            {/* This invisible element helps maintain the layout balance */}
            Showing {totalCount > 0 ? getVisibleRange().start : 0} to{" "}
            {getVisibleRange().end} of {totalCount} organizations
          </div>
        </div>
      )}
    </div>
  );
}
