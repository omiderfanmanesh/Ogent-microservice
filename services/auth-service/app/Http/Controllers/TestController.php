<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class TestController extends Controller
{
    /**
     * A simple test endpoint
     *
     * @return \Illuminate\Http\JsonResponse
     */
    public function index()
    {
        return response()->json([
            'message' => 'Auth Service is working correctly!',
            'status' => 'success',
            'timestamp' => now()->toDateTimeString(),
        ]);
    }
} 