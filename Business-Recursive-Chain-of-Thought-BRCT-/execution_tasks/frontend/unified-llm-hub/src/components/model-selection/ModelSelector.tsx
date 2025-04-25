import React, { useEffect, useState } from "react";
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Paper,
  Grid,
  Chip,
  SelectChangeEvent,
  Tooltip,
  FormHelperText,
} from "@mui/material";
import { useAppDispatch } from "../../hooks/useAppDispatch";
import { useTypedSelector } from "../../hooks/useTypedSelector";
import {
  setSelectedProvider,
  setSelectedModel,
} from "../../store/slices/llmSlice";

interface ModelSelectorProps {
  vertical?: boolean;
  compact?: boolean;
  onChange?: (provider: string, model: string) => void;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({
  vertical = false,
  compact = false,
  onChange,
}) => {
  const dispatch = useAppDispatch();
  const { providers, models, selectedProvider, selectedModel } =
    useTypedSelector((state) => state.llm);

  // Create a local state to handle changes before dispatching to redux
  const [localProvider, setLocalProvider] = useState<string>(
    selectedProvider || ""
  );
  const [localModel, setLocalModel] = useState<string>(selectedModel || "");

  // Filter models by provider
  const filteredModels = models.filter(
    (model) => model.provider === localProvider
  );

  // Update local state when redux state changes
  useEffect(() => {
    if (selectedProvider) {
      setLocalProvider(selectedProvider);
    }
    if (selectedModel) {
      setLocalModel(selectedModel);
    }
  }, [selectedProvider, selectedModel]);

  const handleProviderChange = (event: SelectChangeEvent<string>) => {
    const newProvider = event.target.value;
    setLocalProvider(newProvider);

    // Reset model selection when provider changes
    setLocalModel("");

    // Don't immediately update Redux, wait for model selection
    // unless there's only one model for this provider
    const providerModels = models.filter(
      (model) => model.provider === newProvider
    );
    if (providerModels.length === 1) {
      setLocalModel(providerModels[0].id);
      dispatch(setSelectedProvider(newProvider));
      dispatch(setSelectedModel(providerModels[0].id));

      if (onChange) {
        onChange(newProvider, providerModels[0].id);
      }
    }
  };

  const handleModelChange = (event: SelectChangeEvent<string>) => {
    const newModel = event.target.value;
    setLocalModel(newModel);

    // Update Redux
    dispatch(setSelectedProvider(localProvider));
    dispatch(setSelectedModel(newModel));

    if (onChange) {
      onChange(localProvider, newModel);
    }
  };

  const selectedProviderObj = providers.find((p) => p.id === localProvider);
  const selectedModelObj = models.find((m) => m.id === localModel);

  const getProviderChipColor = (providerId: string) => {
    switch (providerId) {
      case "openai":
        return "#10a37f"; // OpenAI green
      case "anthropic":
        return "#b13dff"; // Anthropic purple
      case "gemini":
        return "#4285f4"; // Google blue
      default:
        return "default";
    }
  };

  if (compact) {
    return (
      <Box>
        <Tooltip
          title={
            <>
              <Typography variant="body2">
                Provider: {selectedProviderObj?.name || "None"}
              </Typography>
              <Typography variant="body2">
                Model: {selectedModelObj?.name || "None"}
              </Typography>
            </>
          }
        >
          <Chip
            label={
              selectedModelObj
                ? `${selectedProviderObj?.name}: ${selectedModelObj?.name}`
                : "Select Model"
            }
            color={selectedProviderObj ? "primary" : "default"}
            onClick={() => {}} // This would open a dialog in a real implementation
            sx={{
              backgroundColor: selectedProviderObj
                ? getProviderChipColor(selectedProviderObj.id)
                : undefined,
              color: selectedProviderObj ? "white" : undefined,
            }}
          />
        </Tooltip>
      </Box>
    );
  }

  return (
    <Box sx={{ width: "100%" }}>
      <Grid container spacing={2} direction={vertical ? "column" : "row"}>
        <Grid item xs={vertical ? 12 : 6}>
          <FormControl fullWidth>
            <InputLabel id="provider-label">Provider</InputLabel>
            <Select
              labelId="provider-label"
              value={localProvider}
              label="Provider"
              onChange={handleProviderChange}
            >
              {providers.map((provider) => (
                <MenuItem key={provider.id} value={provider.id}>
                  {provider.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={vertical ? 12 : 6}>
          <FormControl fullWidth disabled={!localProvider}>
            <InputLabel id="model-label">Model</InputLabel>
            <Select
              labelId="model-label"
              value={localModel}
              label="Model"
              onChange={handleModelChange}
            >
              {filteredModels.map((model) => (
                <MenuItem key={model.id} value={model.id}>
                  {model.name}
                </MenuItem>
              ))}
            </Select>
            {filteredModels.length === 0 && localProvider && (
              <FormHelperText>Please select a provider first</FormHelperText>
            )}
          </FormControl>
        </Grid>
      </Grid>

      {selectedModelObj && !compact && (
        <Paper
          variant="outlined"
          sx={{ mt: 2, p: 1, borderRadius: 1, bgcolor: "background.paper" }}
        >
          <Typography variant="caption" color="text.secondary">
            Selected:
          </Typography>
          <Box sx={{ display: "flex", alignItems: "center", mt: 0.5 }}>
            <Chip
              size="small"
              label={selectedProviderObj?.name}
              sx={{
                mr: 1,
                backgroundColor: getProviderChipColor(localProvider),
                color: "white",
              }}
            />
            <Typography variant="body2">{selectedModelObj.name}</Typography>
          </Box>
          {selectedModelObj.description && (
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ display: "block", mt: 1 }}
            >
              {selectedModelObj.description}
            </Typography>
          )}
        </Paper>
      )}
    </Box>
  );
};

export default ModelSelector;
