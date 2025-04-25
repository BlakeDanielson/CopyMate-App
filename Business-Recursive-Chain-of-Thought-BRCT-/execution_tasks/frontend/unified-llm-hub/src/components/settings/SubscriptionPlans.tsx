import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  CircularProgress,
  Grid,
  Paper,
  Typography,
  useTheme,
} from "@mui/material";
import {
  fetchSubscriptionPlans,
  selectSubscriptionPlans,
  createCheckoutSession,
  selectCheckoutState,
} from "../../store/slices/subscriptionSlice";
import { StoreState } from "../../store/store";
import { AppDispatch } from "../../store/store";

const SubscriptionPlans: React.FC = () => {
  const theme = useTheme();
  const dispatch = useDispatch<AppDispatch>();
  const { data: plans, loading, error } = useSelector(selectSubscriptionPlans);
  const checkoutState = useSelector(selectCheckoutState);
  const currentSubscription = useSelector(
    (state: StoreState) => state.subscription.currentSubscription.data
  );

  useEffect(() => {
    dispatch(fetchSubscriptionPlans());
  }, [dispatch]);

  const handleSubscribe = (planId: string) => {
    dispatch(createCheckoutSession(planId));
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" my={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Paper
        elevation={2}
        sx={{ p: 3, mt: 2, backgroundColor: theme.palette.error.light }}
      >
        <Typography variant="h6" color="error">
          Error loading subscription plans
        </Typography>
        <Typography color="error">{error}</Typography>
      </Paper>
    );
  }

  if (!plans || plans.length === 0) {
    return (
      <Paper elevation={2} sx={{ p: 3, mt: 2 }}>
        <Typography variant="h6" gutterBottom>
          No Subscription Plans Available
        </Typography>
        <Typography variant="body1" color="textSecondary" paragraph>
          There are currently no subscription plans available. Please check back
          later.
        </Typography>
      </Paper>
    );
  }

  return (
    <Box mt={3}>
      <Typography variant="h5" gutterBottom mb={3}>
        Available Subscription Plans
      </Typography>

      <Grid container spacing={3}>
        {plans.map((plan) => {
          const isCurrentPlan = currentSubscription?.planId === plan.id;
          const isCurrentActive =
            isCurrentPlan && currentSubscription?.status === "ACTIVE";

          return (
            <Grid item xs={12} md={4} key={plan.id}>
              <Card
                elevation={3}
                sx={{
                  height: "100%",
                  display: "flex",
                  flexDirection: "column",
                  border: isCurrentPlan
                    ? `2px solid ${theme.palette.primary.main}`
                    : "none",
                }}
              >
                <CardHeader
                  title={plan.name}
                  titleTypographyProps={{ align: "center", variant: "h5" }}
                  sx={{
                    backgroundColor: isCurrentPlan
                      ? theme.palette.primary.main
                      : theme.palette.grey[200],
                    color: isCurrentPlan
                      ? theme.palette.primary.contrastText
                      : theme.palette.text.primary,
                  }}
                />
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "baseline",
                      mb: 2,
                    }}
                  >
                    <Typography
                      component="h2"
                      variant="h3"
                      color="text.primary"
                    >
                      {new Intl.NumberFormat("en-US", {
                        style: "currency",
                        currency: plan.currency,
                      }).format(plan.price / 100)}
                    </Typography>
                    <Typography variant="h6" color="text.secondary">
                      /{plan.interval === "MONTH" ? "mo" : "yr"}
                    </Typography>
                  </Box>

                  <Typography variant="body1" align="center" sx={{ mb: 2 }}>
                    {plan.description ||
                      `Access to all features with ${
                        plan.messageQuota
                      } messages per ${
                        plan.interval === "MONTH" ? "month" : "year"
                      }.`}
                  </Typography>

                  <Typography variant="h6" align="center" sx={{ mt: 3 }}>
                    {plan.messageQuota.toLocaleString()} messages
                  </Typography>

                  {isCurrentPlan && (
                    <Box
                      mt={2}
                      p={1}
                      bgcolor={theme.palette.success.light}
                      borderRadius={1}
                    >
                      <Typography
                        variant="body2"
                        align="center"
                        color="success.dark"
                      >
                        {isCurrentActive
                          ? "Your current plan"
                          : "Your inactive plan"}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
                <CardActions>
                  <Button
                    fullWidth
                    variant={isCurrentPlan ? "outlined" : "contained"}
                    color="primary"
                    disabled={isCurrentActive || checkoutState.loading}
                    onClick={() => handleSubscribe(plan.id)}
                  >
                    {checkoutState.loading ? (
                      <CircularProgress size={24} color="inherit" />
                    ) : isCurrentActive ? (
                      "Current Plan"
                    ) : isCurrentPlan ? (
                      "Reactivate"
                    ) : (
                      "Subscribe"
                    )}
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {checkoutState.error && (
        <Paper
          elevation={1}
          sx={{ p: 2, mt: 3, backgroundColor: theme.palette.error.light }}
        >
          <Typography color="error">{checkoutState.error}</Typography>
        </Paper>
      )}
    </Box>
  );
};

export default SubscriptionPlans;
