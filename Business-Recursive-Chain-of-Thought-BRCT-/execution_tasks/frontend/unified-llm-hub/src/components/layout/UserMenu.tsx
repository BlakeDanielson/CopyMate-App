import React, { useState } from "react";
import {
  Box,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Avatar,
  Typography,
} from "@mui/material";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import SettingsIcon from "@mui/icons-material/Settings";
import LogoutIcon from "@mui/icons-material/Logout";
import { useNavigate } from "react-router-dom";
import { useAppDispatch } from "../../hooks/useAppDispatch";
import { useTypedSelector } from "../../hooks/useTypedSelector";
import { logout } from "../../store/slices/authSlice";

const UserMenu: React.FC = () => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { user } = useTypedSelector((state) => state.auth);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleSettings = () => {
    handleClose();
    navigate("/settings");
  };

  const handleLogout = () => {
    handleClose();
    dispatch(logout());
    navigate("/login");
  };

  return (
    <Box>
      <IconButton
        color="inherit"
        onClick={handleClick}
        aria-controls={open ? "user-menu" : undefined}
        aria-haspopup="true"
        aria-expanded={open ? "true" : undefined}
        edge="end"
        sx={{ ml: 1 }}
      >
        {user ? (
          <Avatar sx={{ width: 32, height: 32 }}>
            {user.email ? user.email.charAt(0).toUpperCase() : "U"}
          </Avatar>
        ) : (
          <AccountCircleIcon />
        )}
      </IconButton>
      <Menu
        id="user-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        MenuListProps={{
          "aria-labelledby": "user-menu-button",
        }}
        transformOrigin={{ horizontal: "right", vertical: "top" }}
        anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
      >
        {user && (
          <>
            <Box sx={{ px: 2, py: 1 }}>
              <Typography variant="subtitle2">{user.email}</Typography>
              <Typography variant="caption" color="text.secondary">
                {user.subscription?.plan || "Free Plan"}
              </Typography>
            </Box>
            <Divider />
          </>
        )}
        <MenuItem onClick={handleSettings}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Settings</ListItemText>
        </MenuItem>
        {user ? (
          <MenuItem onClick={handleLogout}>
            <ListItemIcon>
              <LogoutIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Logout</ListItemText>
          </MenuItem>
        ) : (
          <MenuItem onClick={() => navigate("/login")}>
            <ListItemIcon>
              <AccountCircleIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText>Login</ListItemText>
          </MenuItem>
        )}
      </Menu>
    </Box>
  );
};

export default UserMenu;
