import './css/App.css';
import Header from './Header.js';
import Form from './Form.js';
import { ThemeProvider, createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: "#03d1ff",
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
    <div className="App">
      <Header />
      <Form />
    </div>
    </ThemeProvider>
  );
}

export default App;
