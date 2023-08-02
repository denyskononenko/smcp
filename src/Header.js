import React, {Component} from "react";
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import GitHubIcon from '@mui/icons-material/GitHub';
import DescriptionIcon from '@mui/icons-material/Description';
import AppLogo from './logo.svg';

const linkPaper = "https://arxiv.org/abs/2303.14033";
const linkCode  = "https://github.com/denyskononenko/smcp";

class Form extends Component {
    render(){
        return(
            <AppBar 
                position="static"
                sx={{ backgroundColor: "#494D5f" }}>
                <Toolbar>
                <IconButton
                    size="large"
                    edge="start"
                    color="inherit"
                    aria-label="menu"
                    sx={{ mr: 2 }}>
                    <img src={AppLogo} alt="Logo" />
                </IconButton>

                <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                    <Typography variant="h6" 
                        component="div" 
                        color="#FFFFFF"
                        sx={{ }}>
                        Spin Models for Cuprates Predictor
                    </Typography>
                    <Typography variant="subtitle1" 
                        component="div" 
                        color="#FFFFFF"
                        sx={{ marginLeft: 1 }}>
                        v0.1
                    </Typography>
                </Box>
                <a href={linkPaper} target="_blank" rel="noreferrer">
                    <Button 
                        endIcon={<DescriptionIcon />}
                        size="medium"
                        variant="text">
                        Paper
                    </Button>
                </a>
                <a href={linkCode} target="_blank" rel="noreferrer">
                    <Button 
                        endIcon={<GitHubIcon />} 
                        variant="text"
                        size="medium">
                        Code
                    </Button>
                </a>
                </Toolbar>
            </AppBar>
        );
    }
}

export default Form;