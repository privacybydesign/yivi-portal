"use client";

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

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
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [trustModels, setTrustModels] = useState<string[]>([]);
  const [selectedTrustModel, setSelectedTrustModel] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [view, setView] = useState("all"); // "all", "ap", or "rp"
  
  // Pagination state
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const pageSize = 20; // Fixed page size

  const fetchOrganizations = (page = 1) => {
    setLoading(true);
    // Calculate offset based on page number and page size
    const offset = (page - 1) * pageSize;
    
    axios.get(`http://0.0.0.0:8000/v1/organizations/?limit=${pageSize}&offset=${offset}`)
      .then(response => {
        const data = response.data as PaginationResponse;
        const orgs = data.results;
        setOrganizations(orgs);
        
        // Set pagination data
        setTotalCount(data.count);
        setTotalPages(Math.ceil(data.count / pageSize));
        
        // Extract unique trust models
        const models = [...new Set(orgs.map((org: Organization) => org.trust_model))].filter(Boolean) as string[];
        setTrustModels(models);
        
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching organizations:', error);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchOrganizations(currentPage);
  }, [currentPage]);

  // Handle page change
  const handlePageChange = (newPage: number) => {
    if (newPage > 0 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  // Reset pagination when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [selectedTrustModel, view, searchQuery]);

  // Filter organizations based on selected view and filters
  const getFilteredOrganizations = () => {
    return organizations.filter(org => {
      // Filter by AP/RP status
      if (view === "ap" && !org.is_AP) return false;
      if (view === "rp" && !org.is_RP) return false;
      
      // Filter by trust model
      if (selectedTrustModel !== "all" && org.trust_model !== selectedTrustModel) return false;
      
      // Filter by search query
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          org.name_en.toLowerCase().includes(query) ||
          org.slug.toLowerCase().includes(query)
        );
      }
      
      return true;
    });
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

  // Apply filters and update display
  const handleApplyFilters = () => {
    fetchOrganizations(1); // Reset to first page when applying filters
  };

  if (loading && currentPage === 1) {
    return <div className="text-center py-8">Loading organizations...</div>;
  }

  const filteredOrganizations = getFilteredOrganizations();

  return (
    <div className="container mx-auto p-4">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
        <h1 className="text-2xl font-bold">Organizations</h1>
        
        <div className="flex flex-col md:flex-row gap-4">
          <input
            type="text"
            placeholder="Search organizations..."
            className="px-3 py-2 border rounded-md"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          
          <select 
            value={selectedTrustModel}
            onChange={(e) => setSelectedTrustModel(e.target.value)}
            className="px-3 py-2 border rounded-md"
          >
            <option value="all">All Trust Models</option>
            {trustModels.map(model => (
              <option key={model} value={model}>{model}</option>
            ))}
          </select>
          
          <Button onClick={handleApplyFilters}>
            Apply Filters
          </Button>
        </div>
      </div>
      
      <div className="flex mb-6 border-b">
        <button 
          className={`px-4 py-2 font-medium ${view === "all" ? "border-b-2 border-blue-500 text-blue-600" : "text-gray-600"}`}
          onClick={() => setView("all")}
        >
          All Organizations
        </button>
        <button 
          className={`px-4 py-2 font-medium ${view === "ap" ? "border-b-2 border-blue-500 text-blue-600" : "text-gray-600"}`}
          onClick={() => setView("ap")}
        >
          Attestation Providers
        </button>
        <button 
          className={`px-4 py-2 font-medium ${view === "rp" ? "border-b-2 border-blue-500 text-blue-600" : "text-gray-600"}`}
          onClick={() => setView("rp")}
        >
          Relying Parties
        </button>
      </div>
      
      <Table>
        <TableCaption>
          {view === "all" ? "All Organizations" : 
           view === "ap" ? "Attestation Providers" : "Relying Parties"}
        </TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead className="w-16">Logo</TableHead>
            <TableHead>Name</TableHead>
            <TableHead>Trust Model</TableHead>
            {view === "all" && (
              <>
                <TableHead>AP</TableHead>
                <TableHead>RP</TableHead>
              </>
            )}
          </TableRow>
        </TableHeader>
        <TableBody>
          {loading ? (
            <TableRow>
              <TableCell 
                colSpan={view === "all" ? 5 : 3} 
                className="text-center py-4 text-gray-500"
              >
                Loading...
              </TableCell>
            </TableRow>
          ) : (
            <>
              {filteredOrganizations.map(org => (
                <TableRow key={org.id}>
                  <TableCell>
                    {org.logo ? (
                      <div className="relative h-8 w-8 rounded-full overflow-hidden border border-gray-200">
                        <img 
                          src={`http://0.0.0.0:8000${org.logo}`} 
                          alt={`${org.name_en} logo`} 
                          className="object-cover w-full h-full"
                          onError={(e) => {
                            e.currentTarget.src = "/placeholder-logo.png"; 
                          }}
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
                  {view === "all" && (
                    <>
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
                    </>
                  )}
                </TableRow>
              ))}
              {filteredOrganizations.length === 0 && (
                <TableRow>
                  <TableCell 
                    colSpan={view === "all" ? 5 : 3} 
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
            Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalCount)} of {totalCount} organizations
          </div>
          
          <div className="flex-1 flex justify-center">
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
              >
                Previous
              </Button>
              
              {getPageNumbers().map((page, index) => (
                <Button
                  key={index}
                  variant={page === currentPage ? "default" : "outline"}
                  size="sm"
                  onClick={() => typeof page === 'number' && handlePageChange(page)}
                  disabled={typeof page !== 'number'}
                >
                  {page}
                </Button>
              ))}
              
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                Next
              </Button>
            </div>
          </div>
          
          <div className="invisible text-sm text-gray-500">
            {/* This invisible element helps maintain the layout balance */}
            Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalCount)} of {totalCount} organizations
          </div>
        </div>
      )}
    </div>
  );
}