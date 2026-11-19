import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import { DataGrid } from '@mui/x-data-grid';
import {
  Button,
  IconButton,
  Grid,
  MenuItem,
  Select,
  TextField,
} from '@mui/material';
import { makeStyles } from 'tss-react/mui';
import ClearIcon from '@mui/icons-material/Clear';
import SearchIcon from '@mui/icons-material/Search';

const datagridStyles = makeStyles()({
  root: {
    "& .MuiDataGrid-renderingZone": {
      maxHeight: "none !important"
    },
    "& .MuiDataGrid-cell": {
      lineHeight: "unset !important",
      maxHeight: "none !important",
      whiteSpace: "normal"
    },
    "& .MuiDataGrid-row": {
      maxHeight: "none !important"
    },
    "& .MuiDataGrid-main":{
      height: "30rem !important",
    },
    "& .MuiDataGrid-virtualScroller":{
      height: "30rem !important",
    }
  }
});

function QuickSearchToolbar(props) {
  // const classes = searchStyles();

  return (
    <div style={{ float: 'right' }}>
      <TextField
        variant="standard"
        value={props.value}
        onChange={props.onChange}
        placeholder="Search…"
        InputProps={{
          startAdornment: <SearchIcon fontSize="large" />,
          endAdornment: (
            <IconButton
              title="Clear"
              aria-label="Clear"
              size="large"
              style={{ visibility: props.value ? 'visible' : 'hidden' }}
              onClick={props.clearSearch}
            >
              <ClearIcon />
            </IconButton>
          ),
        }}
        sx={{ 
          marginBottom: '1rem', 
          input: { 
            fontSize: '18px',
          } 
        }}
      />
    </div>
  );
}

QuickSearchToolbar.propTypes = {
  clearSearch: PropTypes.func.isRequired,
  onChange: PropTypes.func.isRequired,
  value: PropTypes.string.isRequired,
};

const useStyles = makeStyles()({
  root: {
    fontweight: 900,
  },
  header: {
    '& .MuiDataGrid-columnHeaderTitleContainer':{
      flexFlow: 'row-reverse',
    },
  }
});

export const RequestsTable = ({ elementId, isOwner }) => {
  const { classes: dgClasses } = datagridStyles();
  const [data, setData] = useState([]);
  const [rows, setRows] = useState(data)
  const [searchText, setSearchText] = useState('');
  const [columnsForEditor, setColumnsForEditor] = useState([]);
  const [columns, setColumns] = useState([
    {
        field: 'user',
        headerName: 'User',
        width: 150,
        editable: false,
        valueGetter: (value, row) => row.system.user.full_name,
    },
    {
      field: 'system',
      headerName: 'Requested by',
      width: 150,
      editable: false,
      valueGetter: (value, row) => row.system.root_element.full_name,
    },
    {
        field: 'status',
        headerName: 'Status',
        width: 150,
        editable: false,
        valueGetter: (value, row) => row.status,
    },
  ]);
  function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
  const requestSearch = (searchValue) => {
    setSearchText(searchValue);
    const searchRegex = new RegExp(escapeRegex(searchValue.toLowerCase()));
    
    const filteredRows = data.filter((row) => {
      return Object.keys(row).some((field) => {
        if(row[field] !== null){
          if(field === 'system'){
            return searchRegex.test(row[field].name.toString().toLowerCase());
          }
          return searchRegex.test(row[field].toString().toLowerCase());
        }
      });
    });
    setRows(filteredRows);
  };

  const handleChange = (status, params, data) => {
    const updatedData = [...data];
    const currentIndex = updatedData.findIndex(item => item.id === params.row.id);
    updatedData[currentIndex].status = status;
    setData(updatedData);
  }

  const handleSubmit = async (params) => {
    const updatedRequest = {
      user: params.row.userId,
      system: params.row.system.id,
      requested_element: params.row.requested_element.id,
      criteria_comment: params.row.criteria_comment,
      criteria_reject_comment: params.row.criteria_reject_comment,
      status: params.row.status,
    }
    const updateRequestResponse = await axios.put(`/api/v2/requests/${params.row.requestId}/`, updatedRequest);
    if(updateRequestResponse.status === 200){
      if(updatedRequest.status === 'Closed') {
        window.location.reload();
      }
    } else {
      console.error("Something went wrong in creating and setting new request to element");
    }
  }
  
  useEffect(() => {
    axios(`/api/v2/elements/${elementId}/retrieveRequests/`).then(response => {
      setData(response.data.requested.filter((item) => item.status != "Closed"));
    });
  }, []);

  useEffect(() => {
    setRows(data);
  }, [data]);

  useEffect(() => {
    setColumnsForEditor([
      {
        field: 'system',
        headerName: 'Requested by',
        type: 'string', 
        width: 150,
        editable: false,
        valueGetter: (value, row) => row.system.name,
      },
      {
        field: 'point_of_contact',
        headerName: 'Point of Contact',
        type: 'string', 
        width: 300,
        editable: false,
        renderCell: (params) => (
          <div>
            {params.row.user_name} {(params.row.user_phone_number) ? `(${params.row.user_phone_number})` : ''}
          </div>
        ),
      },
      {
        field: 'status',
        headerName: 'Status',
        type: 'string', 
        width: 150,
        editable: false,
        valueGetter: (value, row) => row.status,
      },
      {
        field: 'action',
        headerName: 'Action',
        width: 300,
        editable: true,
        type: 'actions',
        renderCell: (params) => (
          <Grid container rowSpacing={1} columnSpacing={{ xs: 1, sm: 2, md: 3 }}>
            {data.length !== 0 && <Grid item xs={6}>
                <Select
                  value={params.row.status}
                  onChange={(event) => handleChange(event.target.value, params, data)}
                  variant="outlined"
                  size="small"
                  sx={{ minWidth: 150, marginTop: '0.4rem', fontSize: '0.875rem' }}
                >
                  {["Open", "Pending", "In Progress", "Approve", "Reject", "Closed"].map((status) => (
                    <MenuItem key={status} value={status}>{status}</MenuItem>
                  ))}
                </Select>
            </Grid>}
            <Grid item xs={6}>
              <Button variant="primary" onClick={() => handleSubmit(params)} sx={{marginTop: '0.8rem'}}>Submit</Button>
            </Grid>
          </Grid>
        ),
      },
    ]);
  }, [data]);

  return (
      <div style={{ maxHeight: '2000px', width: '100%' }}>
          {data !== null && columnsForEditor.length !== 0 && <Grid className="poc-data-grid" sx={{ minHeight: '500px' }}>
          <QuickSearchToolbar value={searchText} onChange={(event) => requestSearch(event.target.value)} clearSearch={() => requestSearch('')}/>
              <div style={{width: "calc(100% - 1rem - 25px)", marginTop: "1rem" }}>
                  <div style={{ width: "100%", marginBottom: "1rem", display: "flex", justifyContent: "space-between" }}>
                      <DataGrid
                        initialState={{ pagination: { paginationModel: { pageSize: 25 } } }}
                        className={dgClasses.root}
                        autoHeight={true}
                        density="compact"
                        rows={rows}
                        columns={isOwner ? columnsForEditor : columns}
                        pageSizeOptions={[25]}
                        rowHeight={50}
                        checkboxSelection
                        // onSelectionModelChange={(selectionModel, details) => {
                        //   console.log(selectionModel, details);
                        // }}
                        // disableSelectionOnClick
                        sx={{ 
                          fontSize: '14px',
                          '& .MuiDataGrid-columnHeaderTitle':{
                              fontWeight: 600,
                          },
                        }}
                      />
                  </div>
              </div>
          </Grid>
          }
      </div>
  )
}