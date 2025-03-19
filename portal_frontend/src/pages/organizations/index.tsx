"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/src/components/ui/table";
import { Badge } from "@/src/components/ui/badge";
import { Button } from "@/src/components/ui/button";
import { Checkbox } from "@/src/components/ui/checkbox";
import Image from "next/image";
import { axiosInstance } from '@/src/services/axiosInstance';
import getConfig from 'next/config';

// Define Organization type
interface Organization {
  id: string;
  name_en: string;
  name_nl: string;
  slug: string;
  logo: string;
  is_RP: boolean;
  is_AP: boolean;
  trust_model: string;
}

// Define pagination response interface
interface PaginationResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Organization[];
}

export default function OrganizationsPage() {
  const { publicRuntimeConfig } = getConfig();
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [trustModels, setTrustModels] = useState<string[]>([]);
  const [selectedTrustModel, setSelectedTrustModel] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [isAP, setIsAP] = useState(false);
  const [isRP, setIsRP] = useState(false);
  const [applyingFilters, setApplyingFilters] = useState(false);
  
  // Pagination state
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const pageSize = 20; // Fixed page size

  // Function to fetch organizations with pagination
  const fetchOrganizations = (page = 1, applyFilters = false) => {
    setLoading(true);
    const offset = (page - 1) * pageSize;
    
    // Base URL with pagination
    let url = `/v1/organizations/?limit=${pageSize}&offset=${offset}`;
    
    // Only add filters if applyFilters is true
    if (applyFilters) {
      // Add search if present
      if (searchQuery && searchQuery.trim() !== '') {
        url += `&search=${encodeURIComponent(searchQuery.trim())}`;
      }
      
      // Add trust model filter
      if (selectedTrustModel !== "all") {
        url += `&trust_model=${encodeURIComponent(selectedTrustModel)}`;
      }
    }
    
    console.log("Fetching organizations:", url);
    
    axiosInstance.get(url)
      .then(response => {
        const data = response.data as PaginationResponse;
        let orgs = data.results;
        
        // Filter by AP/RP client-side if needed
        if (applyFilters && (isAP || isRP)) {
          if (isAP) {
            orgs = orgs.filter(org => org.is_AP === true);
          }
          
          if (isRP) {
            orgs = orgs.filter(org => org.is_RP === true);
          }
          
          // For filtered results, we need to adjust the pagination
          setTotalCount(orgs.length);
          setTotalPages(Math.ceil(orgs.length / pageSize));
        } else {
          // For regular pagination (server-side), use the counts from the response
          setTotalCount(data.count);
          setTotalPages(Math.ceil(data.count / pageSize));
        }
        
        setOrganizations(orgs);
        
        // Extract trust models if not already done
        if (trustModels.length === 0) {
          const models = [...new Set(data.results.map(org => org.trust_model))].filter(Boolean);
          setTrustModels(models);
        }
        
        setLoading(false);
        setApplyingFilters(false);
      })
      .catch(error => {
        console.error('Error fetching organizations:', error);
        setLoading(false);
        setApplyingFilters(false);
      });
  };

  // Fetch organizations on initial load and page changes
  useEffect(() => {
    // If we're applying filters, don't refetch on page change
    if (!applyingFilters) {
      fetchOrganizations(currentPage, false);
    }
  }, [currentPage]);

  // Function to apply filters
  const applyFilters = () => {
    setApplyingFilters(true);
    setCurrentPage(1);
    fetchOrganizations(1, true);
  };

  // Handle checkbox changes
  const handleAPChange = (checked: boolean) => {
    setIsAP(checked);
    // Don't apply filters immediately - wait for Apply Filters button click
  };

  const handleRPChange = (checked: boolean) => {
    setIsRP(checked);
    // Don't apply filters immediately - wait for Apply Filters button click
  };

  // Handle page change
  const handlePageChange = (newPage: number) => {
    if (newPage > 0 && newPage <= totalPages) {
      setCurrentPage(newPage);
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
    const start = ((currentPage - 1) * pageSize) + 1;
    const end = Math.min(currentPage * pageSize, totalCount);
    return { start, end };
  };

  return (
    <div className="container mx-auto p-4">
      <div className="flex flex-col gap-6 mb-6">
        <h1 className="text-2xl font-bold">Organizations</h1>
        
        <div className="border rounded-md p-4 bg-gray-50">
          <h2 className="text-lg font-medium mb-4">Filters</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label htmlFor="search" className="block text-sm font-medium mb-1">Search</label>
              <input
                id="search"
                type="text"
                placeholder="Search organizations..."
                className="w-full px-3 py-2 border rounded-md"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && applyFilters()}
              />
            </div>
            
            <div>
              <label htmlFor="trustModel" className="block text-sm font-medium mb-1">Trust Model</label>
              <select 
                id="trustModel"
                value={selectedTrustModel}
                onChange={(e) => setSelectedTrustModel(e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="all">All Trust Models</option>
                {trustModels.map(model => (
                  <option key={model} value={model}>{model}</option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-6 mb-4">
            <div className="flex items-center space-x-2 p-2 rounded hover:bg-gray-100">
              <Checkbox 
                id="isAP" 
                checked={isAP} 
                onCheckedChange={(checked) => handleAPChange(checked === true)}
              />
              <label 
                htmlFor="isAP" 
                className="text-sm font-medium leading-none cursor-pointer"
                onClick={() => handleAPChange(!isAP)}
              >
                Attestation Provider
              </label>
            </div>
            
            <div className="flex items-center space-x-2 p-2 rounded hover:bg-gray-100">
              <Checkbox 
                id="isRP" 
                checked={isRP} 
                onCheckedChange={(checked) => handleRPChange(checked === true)}
              />
              <label 
                htmlFor="isRP" 
                className="text-sm font-medium leading-none cursor-pointer"
                onClick={() => handleRPChange(!isRP)}
              >
                Relying Party
              </label>
            </div>
          </div>
          
          <Button 
            onClick={applyFilters} 
            disabled={loading || applyingFilters}
            className="w-full md:w-auto"
          >
            Apply Filters
          </Button>
          
          {(isAP || isRP || selectedTrustModel !== "all" || searchQuery) && (
            <div className="mt-4 text-sm text-blue-600">
              Filtering: 
              {searchQuery && ` Search: "${searchQuery}"`}
              {selectedTrustModel !== "all" && ` Trust Model: ${selectedTrustModel}`}
              {isAP && " | Attestation Providers"}
              {isRP && " | Relying Parties"}
            </div>
          )}
        </div>
      </div>
      
      <Table>
        <TableCaption>
          {!loading && !applyingFilters && (
            <>
              Showing {totalCount > 0 ? getVisibleRange().start : 0} to {getVisibleRange().end} of {totalCount} organizations
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
              <TableCell 
                colSpan={5} 
                className="text-center py-4 text-gray-500"
              >
                {applyingFilters ? "Applying filters..." : "Loading organizations..."}
              </TableCell>
            </TableRow>
          ) : (
            <>
              {organizations.length > 0 ? (
                organizations.map(org => (
                  <TableRow key={org.id}>
                    <TableCell>
                      {org.logo ? (
                        <div className="relative h-8 w-8 rounded-full overflow-hidden border border-gray-200">
                          <Image 
                            src={`${publicRuntimeConfig.API_ENDPOINT}${org.logo}`}
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
                      <Link href={`/organizations/${org.id}`} className="hover:text-blue-600">
                        {org.name_en}
                      </Link>
                    </TableCell>
                    <TableCell>{org.trust_model}</TableCell>
                    <TableCell>
                      {org.is_AP === true ? (
                        <Badge className="bg-green-100 text-green-800">Yes</Badge>
                      ) : (
                        <Badge variant="outline">No</Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      {org.is_RP === true ? (
                        <Badge className="bg-blue-100 text-blue-800">Yes</Badge>
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
            Showing {totalCount > 0 ? getVisibleRange().start : 0} to {getVisibleRange().end} of {totalCount} organizations
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
                  onClick={() => typeof page === 'number' && handlePageChange(page)}
                  disabled={typeof page !== 'number' || loading}
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
            Showing {totalCount > 0 ? getVisibleRange().start : 0} to {getVisibleRange().end} of {totalCount} organizations
          </div>
        </div>
      )}
    </div>
  );
}