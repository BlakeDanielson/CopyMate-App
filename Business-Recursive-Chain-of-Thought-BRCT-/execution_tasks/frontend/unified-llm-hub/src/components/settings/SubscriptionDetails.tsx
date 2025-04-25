import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  Box,
  Button,
  Card,
  CircularProgress,
  Divider,
  Grid,
  LinearProgress,
  Paper,
  Typography,
  useTheme,
} from "@mui/material";
import {
  selectCurrentSubscription,
  selectSubscriptionQuota,
  fetchCurrentSubscription,
  fetchSubscriptionQuota,
  openCustomerPortal,
} from "../../store/slices/subscriptionSlice";
import { StoreState } from "../../store/store";
import { AppDispatch } from "../../store/store";

const SubscriptionDetails: React.FC = () => {
  const theme = useTheme();
  const dispatch = useDispatch<AppDispatch>();
  const isAuthenticated = useSelector(
    (state: StoreState) => state.auth.isAuthenticated
  );
  const {
    data: subscription,
    loading: subLoading,
    error: subError,
  } = useSelector(selectCurrentSubscription);
  const {
    data: quota,
    loading: quotaLoading,
    error: quotaError,
  } = useSelector(selectSubscriptionQuota);

  useEffect(() => {
    if (isAuthenticated) {
      dispatch(fetchCurrentSubscription());
      dispatch(fetchSubscriptionQuota());
    }
  }, [dispatch, isAuthenticated]);

  const handleManageSubscription = () => {
    dispatch(openCustomerPortal());
  };

  const formatDate = (date: Date | string | undefined) => {
    if (!date) return "N/A";
    return new Date(date).toLocaleDateString();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "ACTIVE":
        return theme.palette.success.main;
      case "PAST_DUE":
        return theme.palette.warning.main;
      case "CANCELED":
        return theme.palette.error.main;
      case "TRIAL":
        return theme.palette.info.main;
      default:
        return theme.palette.text.secondary;
    }
  };

  if (subLoading || quotaLoading) {
    return (
      <Box display="flex" justifyContent="center" my={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (subError || quotaError) {
    return (
      <Paper
        elevation={2}
        sx={{ p: 3, mt: 2, backgroundColor: theme.palette.error.light }}
      >
        <Typography variant="h6" color="error">
          Error loading subscription details
        </Typography>
        <Typography color="error">{subError || quotaError}</Typography>
      </Paper>
    );
  }

  if (!subscription) {
    return (
      <Paper elevation={2} sx={{ p: 3, mt: 2 }}>
        <Typography variant="h6" gutterBottom>
          No Active Subscription
        </Typography>
        <Typography variant="body1" color="textSecondary" paragraph>
          You currently don't have an active subscription plan. Subscribe to a
          plan to get access to more features and increased usage limits.
        </Typography>
      </Paper>
    );
  }

  return (
    <Card elevation={2} sx={{ p: 3, mt: 2 }}>
      <Typography variant="h5" gutterBottom>
        Subscription Details
      </Typography>

      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} sm={6}>
          <Typography variant="subtitle1">Plan</Typography>
          <Typography variant="h6">{subscription.plan.name}</Typography>
        </Grid>

        <Grid item xs={12} sm={6}>
          <Typography variant="subtitle1">Status</Typography>
          <Typography
            variant="h6"
            sx={{ color: getStatusColor(subscription.status) }}
          >
            {subscription.status.replace("_", " ")}
          </Typography>
        </Grid>

        <Grid item xs={12} sm={6}>
          <Typography variant="subtitle1">Price</Typography>
          <Typography variant="h6">
            {new Intl.NumberFormat("en-US", {
              style: "currency",
              currency: subscription.plan.currency,
            }).format(subscription.plan.price / 100)}
            {" / "}
            {subscription.plan.interval === "MONTH" ? "month" : "year"}
          </Typography>
        </Grid>

        <Grid item xs={12} sm={6}>
          <Typography variant="subtitle1">Renews</Typography>
          <Typography variant="h6">
            {formatDate(subscription.currentPeriodEnd)}
          </Typography>
        </Grid>
      </Grid>

      <Divider sx={{ my: 3 }} />

      {quota && (
        <>
          <Typography variant="h5" gutterBottom>
            Usage Statistics
          </Typography>

          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Message Quota Usage: {quota.usedQuota} / {quota.totalQuota} (
                {quota.usagePercentage}%)
              </Typography>
              <LinearProgress
                variant="determinate"
                value={Math.min(quota.usagePercentage, 100)}
                color={quota.usagePercentage > 80 ? "warning" : "primary"}
                sx={{ height: 10, borderRadius: 5 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle1">Messages Remaining</Typography>
              <Typography variant="h6">{quota.remainingQuota}</Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle1">Current Period</Typography>
              <Typography variant="h6">
                {formatDate(quota.currentPeriodStart)} -{" "}
                {formatDate(quota.currentPeriodEnd)}
              </Typography>
            </Grid>
          </Grid>
        </>
      )}

      <Box display="flex" justifyContent="flex-end" mt={3}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleManageSubscription}
          disabled={subscription.status === "CANCELED"}
        >
          Manage Subscription
        </Button>
      </Box>
    </Card>
  );
};

export default SubscriptionDetails;
