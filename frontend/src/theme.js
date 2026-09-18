import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    primary: {
      main: "#00695C",
    },
    secondary: {
      main: "#2E7D32",
    },
    background: {
      default: "#f5f5f5",
    },
  },

  typography: {
    fontFamily: "Roboto, Arial, sans-serif",
  },

  shape: {
    borderRadius: 8,
  },
});

export default theme;