package com.landregistry.admin;

import com.landregistry.security.SecurityUtil;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/admin")
public class AdminController {
    private final AdminService adminService;

    public AdminController(AdminService adminService) {
        this.adminService = adminService;
    }

    @GetMapping("/dashboard")
    public AdminService.Dashboard dashboard() {
        return adminService.dashboard(SecurityUtil.current());
    }

    @PostMapping("/applications/{id}/approve")
    public AdminService.OfficerView approve(@PathVariable Long id) {
        return adminService.approve(SecurityUtil.current(), id);
    }

    @PostMapping("/applications/{id}/reject")
    public AdminService.ApplicationView reject(
            @PathVariable Long id,
            @RequestParam(required = false, defaultValue = "") String remarks
    ) {
        return adminService.reject(SecurityUtil.current(), id, remarks);
    }
}
