import React, { useEffect, useState } from "react";
import { useAppDispatch } from "../../hooks/useAppDispatch";
import { useTypedSelector } from "../../hooks/useTypedSelector";
import {
  fetchDashboardData,
  fetchAvailableFilters,
  setTimeWindow,
} from "../../store/slices/analyticsSlice";
import { TimeWindow } from "../../interfaces/analytics";
import {
  Box,
  Card,
  CardContent,
  CircularProgress,
  Container,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Typography,
  Divider,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";

/**
 * Analytics Dashboard Component
 * Displays system performance metrics for administrators
 */
const AnalyticsDashboard: React.FC = () => {
  const dispatch = useAppDispatch();
  const { dashboard, filters, availableFilters } = useTypedSelector(
    (state) => state.analytics
  );
  const [selectedTimeWindow, setSelectedTimeWindow] = useState<TimeWindow>(
    TimeWindow.DAY
  );

  // Fetch dashboard data and available filters on mount
  useEffect(() => {
    dispatch(fetchAvailableFilters());
    dispatch(fetchDashboardData({ timeWindow: selectedTimeWindow }));
  }, [dispatch, selectedTimeWindow]);

  // Handle time window change
  const handleTimeWindowChange = (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | any
  ) => {
    const newTimeWindow = event.target.value as TimeWindow;
    setSelectedTimeWindow(newTimeWindow);
    dispatch(setTimeWindow(newTimeWindow));
    dispatch(fetchDashboardData({ timeWindow: newTimeWindow }));
  };

  // Loading state
  if (dashboard.loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        height="70vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  // Error state
  if (dashboard.error) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        height="70vh"
      >
        <Typography color="error" variant="h6">
          Error loading analytics data: {dashboard.error}
        </Typography>
      </Box>
    );
  }

  // No data state
  if (!dashboard.data) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        height="70vh"
      >
        <Typography variant="h6">No analytics data available yet.</Typography>
      </Box>
    );
  }

  return (
    <Container maxWidth="xl">
      <Box mt={4} mb={6}>
        <Typography variant="h4" component="h1" gutterBottom>
          System Performance Analytics
        </Typography>
        <Typography variant="subtitle1" color="textSecondary">
          Monitor system performance metrics and LLM provider efficiency
        </Typography>
      </Box>

      {/* Time Window Selector */}
      <Box mb={4}>
        <FormControl variant="outlined" style={{ minWidth: 200 }}>
          <InputLabel id="time-window-select-label">Time Window</InputLabel>
          <Select
            labelId="time-window-select-label"
            id="time-window-select"
            value={selectedTimeWindow}
            onChange={handleTimeWindowChange as any}
            label="Time Window"
          >
            <MenuItem value={TimeWindow.HOUR}>Hourly</MenuItem>
            <MenuItem value={TimeWindow.DAY}>Daily</MenuItem>
            <MenuItem value={TimeWindow.WEEK}>Weekly</MenuItem>
            <MenuItem value={TimeWindow.MONTH}>Monthly</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Key Performance Metrics */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                API Performance
              </Typography>
              <Typography variant="h4">
                {Math.round(dashboard.data.overallApiSuccessRate * 100)}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Overall API success rate
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                LLM Provider Performance
              </Typography>
              <Typography variant="h4">
                {Math.round(dashboard.data.overallLlmSuccessRate * 100)}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Overall LLM success rate
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Top Endpoints Table */}
      <Typography variant="h5" gutterBottom mt={4}>
        Top API Endpoints
      </Typography>
      <TableContainer component={Paper} sx={{ mb: 4 }}>
        <Table aria-label="top endpoints table">
          <TableHead>
            <TableRow>
              <TableCell>Endpoint</TableCell>
              <TableCell align="right">Requests</TableCell>
              <TableCell align="right">Avg. Response Time (ms)</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {dashboard.data.topEndpoints.map(
              (endpoint: {
                endpoint: string;
                requestCount: number;
                averageResponseTime: number;
              }) => (
                <TableRow key={endpoint.endpoint}>
                  <TableCell component="th" scope="row">
                    {endpoint.endpoint}
                  </TableCell>
                  <TableCell align="right">{endpoint.requestCount}</TableCell>
                  <TableCell align="right">
                    {Math.round(endpoint.averageResponseTime)}
                  </TableCell>
                </TableRow>
              )
            )}
            {dashboard.data.topEndpoints.length === 0 && (
              <TableRow>
                <TableCell colSpan={3} align="center">
                  No endpoint data available
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Top LLM Models Table */}
      <Typography variant="h5" gutterBottom mt={4}>
        Top LLM Models
      </Typography>
      <TableContainer component={Paper}>
        <Table aria-label="top models table">
          <TableHead>
            <TableRow>
              <TableCell>Provider</TableCell>
              <TableCell>Model</TableCell>
              <TableCell align="right">Requests</TableCell>
              <TableCell align="right">Avg. Duration (ms)</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {dashboard.data.topModels.map(
              (model: {
                provider: string;
                model: string;
                requestCount: number;
                averageDuration: number;
              }) => (
                <TableRow key={`${model.provider}-${model.model}`}>
                  <TableCell>{model.provider}</TableCell>
                  <TableCell>{model.model}</TableCell>
                  <TableCell align="right">{model.requestCount}</TableCell>
                  <TableCell align="right">
                    {Math.round(model.averageDuration)}
                  </TableCell>
                </TableRow>
              )
            )}
            {dashboard.data.topModels.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} align="center">
                  No model data available
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default AnalyticsDashboard;
