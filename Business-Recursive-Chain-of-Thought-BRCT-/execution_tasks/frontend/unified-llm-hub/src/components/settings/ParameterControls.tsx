import React, { useState, useEffect } from "react";
import {
  Box,
  Slider,
  Typography,
  Grid,
  TextField,
  FormControl,
  FormHelperText,
  Paper,
  Tooltip,
  IconButton,
} from "@mui/material";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import ReplayIcon from "@mui/icons-material/Replay";
import { useAppDispatch } from "../../hooks/useAppDispatch";
import { updateParameters } from "../../store/slices/llmSlice";
import { LLMParameters } from "../../interfaces/llm";

interface ParameterControlsProps {
  vertical?: boolean;
  compact?: boolean;
  initialValues?: LLMParameters;
  onChange?: (params: LLMParameters) => void;
}

const DEFAULT_PARAMETERS: LLMParameters = {
  temperature: 0.7,
  maxTokens: 2000,
  topP: 0.9,
};

const ParameterControls: React.FC<ParameterControlsProps> = ({
  vertical = true,
  compact = false,
  initialValues,
  onChange,
}) => {
  const dispatch = useAppDispatch();

  // Set up state with initial values or defaults
  const [temperature, setTemperature] = useState(
    initialValues?.temperature || DEFAULT_PARAMETERS.temperature
  );
  const [maxTokens, setMaxTokens] = useState(
    initialValues?.maxTokens || DEFAULT_PARAMETERS.maxTokens
  );
  const [topP, setTopP] = useState(
    initialValues?.topP || DEFAULT_PARAMETERS.topP
  );

  // Update local state when initialValues prop changes
  useEffect(() => {
    if (initialValues) {
      setTemperature(initialValues.temperature);
      setMaxTokens(initialValues.maxTokens);
      setTopP(initialValues.topP);
    }
  }, [initialValues]);

  // Helper function to apply changes to Redux and trigger onChange callback
  const applyChanges = () => {
    const params = { temperature, maxTokens, topP };
    dispatch(updateParameters(params));
    if (onChange) {
      onChange(params);
    }
  };

  // Parameter change handlers
  const handleTemperatureChange = (_: Event, value: number | number[]) => {
    const newValue = Array.isArray(value) ? value[0] : value;
    setTemperature(newValue);
  };

  const handleTemperatureChangeCommitted = () => {
    applyChanges();
  };

  const handleMaxTokensChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (!isNaN(value) && value >= 1) {
      setMaxTokens(value);
    }
  };

  const handleMaxTokensBlur = () => {
    applyChanges();
  };

  const handleTopPChange = (_: Event, value: number | number[]) => {
    const newValue = Array.isArray(value) ? value[0] : value;
    setTopP(newValue);
  };

  const handleTopPChangeCommitted = () => {
    applyChanges();
  };

  const handleReset = () => {
    setTemperature(DEFAULT_PARAMETERS.temperature);
    setMaxTokens(DEFAULT_PARAMETERS.maxTokens);
    setTopP(DEFAULT_PARAMETERS.topP);
    dispatch(updateParameters(DEFAULT_PARAMETERS));
    if (onChange) {
      onChange(DEFAULT_PARAMETERS);
    }
  };

  const renderParameterControl = (
    label: string,
    value: number,
    min: number,
    max: number,
    step: number,
    onChange: (event: Event, value: number | number[]) => void,
    onChangeCommitted: (
      event: React.SyntheticEvent | Event,
      value: number | number[]
    ) => void,
    tooltip: string
  ) => (
    <Box sx={{ mb: compact ? 1 : 2 }}>
      <Box sx={{ display: "flex", alignItems: "center", mb: 0.5 }}>
        <Typography
          variant={compact ? "caption" : "subtitle2"}
          gutterBottom={!compact}
        >
          {label}: {value}
        </Typography>
        <Tooltip title={tooltip}>
          <IconButton size="small" sx={{ ml: 0.5 }}>
            <InfoOutlinedIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
      <Slider
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={onChange}
        onChangeCommitted={onChangeCommitted}
        valueLabelDisplay="auto"
        size={compact ? "small" : "medium"}
      />
    </Box>
  );

  if (compact) {
    return (
      <Paper sx={{ p: 1.5, borderRadius: 1 }}>
        {renderParameterControl(
          "Temperature",
          temperature,
          0,
          1,
          0.01,
          handleTemperatureChange,
          handleTemperatureChangeCommitted,
          "Controls randomness: Lower values are more focused and deterministic, higher values are more creative and diverse."
        )}
        {renderParameterControl(
          "Top P",
          topP,
          0,
          1,
          0.01,
          handleTopPChange,
          handleTopPChangeCommitted,
          "Nucleus sampling: Lower values make the output more focused and deterministic, higher values allow for more creative exploration."
        )}
        <Box sx={{ display: "flex", alignItems: "center", mb: 0.5 }}>
          <Typography variant="caption" gutterBottom>
            Max Tokens: {maxTokens}
          </Typography>
          <Tooltip title="Maximum number of tokens to generate in the response.">
            <IconButton size="small" sx={{ ml: 0.5 }}>
              <InfoOutlinedIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper variant="outlined" sx={{ p: 2, borderRadius: 1 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h6">Model Parameters</Typography>
        <Tooltip title="Reset to default values">
          <IconButton size="small" onClick={handleReset}>
            <ReplayIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={2} direction={vertical ? "column" : "row"}>
        <Grid item xs={vertical ? 12 : 6}>
          {renderParameterControl(
            "Temperature",
            temperature,
            0,
            1,
            0.01,
            handleTemperatureChange,
            handleTemperatureChangeCommitted,
            "Controls randomness: Lower values are more focused and deterministic, higher values are more creative and diverse."
          )}

          {renderParameterControl(
            "Top P",
            topP,
            0,
            1,
            0.01,
            handleTopPChange,
            handleTopPChangeCommitted,
            "Nucleus sampling: Lower values make the output more focused and deterministic, higher values allow for more creative exploration."
          )}
        </Grid>
        <Grid item xs={vertical ? 12 : 6}>
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 0.5 }}>
              <Typography variant="subtitle2" gutterBottom>
                Max Tokens
              </Typography>
              <Tooltip title="Maximum number of tokens to generate in the response.">
                <IconButton size="small" sx={{ ml: 0.5 }}>
                  <InfoOutlinedIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
            <TextField
              fullWidth
              type="number"
              value={maxTokens}
              onChange={handleMaxTokensChange}
              onBlur={handleMaxTokensBlur}
              inputProps={{ min: 1, max: 8192 }}
              variant="outlined"
              size="small"
            />
            <FormHelperText>Limits response length (1-8192)</FormHelperText>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default ParameterControls;
